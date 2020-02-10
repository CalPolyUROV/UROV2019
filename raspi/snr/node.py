from collections import deque
from typing import List, Union

import settings
from snr.datastore import Datastore
from snr.task import SomeTasks, Task, TaskPriority
from snr.utils.utils import sleep
from snr.profiler import Profiler, Timer
from snr.utils.debug import Debugger


class Node:
    def __init__(self, debugger: Debugger,
                 role: str, mode: str,
                 factories: list):
        self.dbg = debugger.debug
        self.role = role
        self.mode = mode
        self.task_queue = deque()
        self.datastore = Datastore(self.dbg)

        self.endpoints = []
        self.task_producers = []

        self.profiler = None
        if settings.ENABLE_PROFILING:
            self.profiler = Profiler(self.dbg)

        self.terminate_flag = False  # Whether to exit main loop

        self.assign_node_ip()

        self.add_endpoints(factories)
        self.dbg("framework",
                 "Initialized with  {} endpoints",
                 [len(self.endpoints)])

    def add_endpoints(self, factories: List):
        self.dbg("framework_verbose", "Adding {} components", [len(factories)])
        for f in factories:
            endpoint = f.get(self)
            if endpoint is not None:
                self.endpoints.append(endpoint)
                if endpoint.task_producers:
                    for fn in endpoint.task_producers:
                        self.task_producers.append(fn)

            self.dbg("framework_verbose", "{} added {}", [f, endpoint])

    def assign_node_ip(self):
        ip = "localhost"
        if not self.mode == "debug":
            if self.role == "robot":
                ip = settings.ROBOT_IP
            elif self.role == "topside":
                ip = settings.TOPSIDE_IP
            else:
                # Panic
                self.dbg("node",
                         "Node role {} not recognized. Counld not select IP",
                         [self.role],
                         )
        self.dbg("node", "Assigned {} node ip: {}", [self.role, ip])
        self.datastore.store("node_ip_address", ip)

    def get_remote_ip(self):
        if not self.mode == "debug":
            if self.role == "robot":
                return settings.TOPSIDE_IP
            if self.role == "topside":
                return settings.ROBOT_IP
            # Panic
            self.dbg("node",
                     "Node role {} not recognized. Counld not get remote IP",
                     [self.role])
        return "localhost"

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            self.dbg("schedule_verbose", "Task queue: \n{}",
                     [self.repr_task_queue()])
            sleep(0.030)
        self.terminate()

    def get_new_tasks(self):
        """Retrieve tasks from endpoints and queue them.
        """
        # new_tasks = [e.get_new_tasks() for e in self.endpoints]
        for task_producer in self.task_producers:
            t = task_producer()
            if t and (isinstance(t, Task) or
                      (isinstance(t, List) and
                       len(t) > 0)):
                self.dbg("schedule_new_tasks",
                         "Produced task: {} from {}",
                         [t, task_producer.__module__])
                self.schedule_task(t)

    def execute_task(self, t: Task):
        """Execute the given task

        Note that the task is pass in and can be provided on the fly rather
        than needing to be in the queue.
        """
        if not t:
            self.dbg("execute_task", "Tried to execute None")
            return

        task_result = []

        for e in self.endpoints:
            handler = e.task_handlers.get(t.task_type)
            result = None
            if handler is not None:
                if self.profiler is None:
                    result = handler(t)
                else:
                    result = self.profiler.time(f"{t.task_type}:{e.name}",
                                                lambda: handler(t))
            if result:
                task_result.append(result)

        self.dbg("schedule_verbose",
                 "Task execution resulted in {} new tasks",
                 [len(list(task_result))])
        if task_result:
            # Only procede if not empty
            self.schedule_task(task_result)

    def set_terminate_flag(self):
        # self.datastore.store("node_exit_reason", reason)
        self.terminate_flag = True

    def terminate(self):
        """Execute actions needed to deconstruct a Node
        """
        for e in self.endpoints:
            e.set_terminate_flag()

        for e in self.endpoints:
            e.join()

        self.datastore.terminate()

        if self.profiler is not None:
            self.profiler.terminate()
        self.dbg("framework", "Node terminated")

    def step_task(self):
        # Get the next task to execute
        t = self.get_next_task()
        self.execute_task(t)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return len(self.task_queue) > 0

    def schedule_task(self, t: SomeTasks):
        """ Adds a Task or a list of Tasks to the node's queue
        """
        if not t:  # t is False if None or empty
            if t is None:
                self.dbg("schedule_warning", "Cannot schedule None")
            elif isinstance(t, list):
                self.dbg("schedule_warning", "Cannot schedule empty list")
            return

        if isinstance(t, list):
            # Recursively handle lists
            self.dbg("schedule_verbose",
                     "Recursively scheduling list of {} tasks",
                     [len(t)])
            for item in t:
                self.dbg("schedule_verbose",
                         "Recursively scheduling item {}",
                         [item])
                self.schedule_task(item)
            return

        if not isinstance(t, Task):
            # Handle non task objects
            self.dbg("schedule_warning",
                     "Cannot schedule {} object {}", [type(t), t])
            return

        # Handle normal tasks
        self.dbg("schedule_verbose", "Scheduling task {}", [t])
        if t.priority == TaskPriority.high:
            self.task_queue.append(t)  # High priotity at front (right)
        elif t.priority == TaskPriority.normal:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
            # TODO:  insert normal priority in between high and low
        elif t.priority == TaskPriority.low:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
        else:
            self.dbg("schedule", "Cannot schedule task with priority: {}",
                     [t.priority])

    def get_next_task(self) -> Union[Task, None]:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            self.dbg("schedule_event", "Ran out of tasks, getting more")
            self.get_new_tasks()
        self.dbg(
            "schedule_verbose", "Popping task, {} remaining", [
                len(self.task_queue) - 1]
        )
        return self.task_queue.pop()

    def store_data(self, key: str, data):
        self.datastore.store(key, data)

    def get_data(self, key: str):
        return self.datastore.get(key)

    def use_data(self, key: str):
        return self.datastore.use(key)

    def repr_task_queue(self) -> str:
        s = ""
        for t in self.task_queue:
            s = s + "\n\t" + str(t)
        return s
