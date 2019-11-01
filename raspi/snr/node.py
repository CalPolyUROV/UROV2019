from collections import deque
from time import time
from typing import List, Union

import settings
from snr.datastore import Datastore
from snr.task import SomeTasks, Task, TaskPriority
from snr.utils import debug
from snr.profiler import Profiler, Timer


class Node:
    def __init__(self, role: str, mode: str, factories: list):
        self.role = role
        self.mode = mode
        self.task_queue = deque()
        self.datastore = Datastore()

        self.endpoints = []

        self.profiler = None
        if settings.ENABLE_PROFILING:
            self.profiler = Profiler()

        self.terminate_flag = False  # Whether to exit main loop

        self.assign_node_ip()

        self.add_endpoints(factories)
        debug("framework",
              "Initialized with  {} endpoints",
              [len(self.endpoints)])

    def add_endpoints(self, factories: List):
        debug("framework_verbose", "Adding {} components", [len(factories)])
        for f in factories:
            endpoint = f.get(self)
            if endpoint is not None:
                self.endpoints.append(endpoint)

            debug("framework_verbose", "Factory {} added {}", [f, endpoint])

    def assign_node_ip(self):
        ip = "localhost"
        if not self.mode == "debug":
            if self.role == "robot":
                ip = settings.ROBOT_IP
            elif self.role == "topside":
                ip = settings.TOPSIDE_IP
            else:
                # Panic
                debug(
                    "node",
                    "Node role {} not recognized. Counld not select IP",
                    [self.role],
                )
        debug("node", "Assigned {} node ip: {}", [self.role, ip])
        self.datastore.store("node_ip_address", ip) 

    def get_remote_ip(self):
        if not self.mode == "debug":
            if self.role == "robot":
                return settings.TOPSIDE_IP
            if self.role == "topside":
                return settings.ROBOT_IP
            # Panic
            debug("node",
                  "Node role {} not recognized. Counld not get remote IP",
                  [self.role])
        return "localhost"

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            debug("schedule_verbose", "Task queue: \n{}",
                  [self.repr_task_queue()])
        self.terminate()

    def get_new_tasks(self):
        """Retrieve tasks from endpoints and queue them.
        """
        # new_tasks = [e.get_new_tasks() for e in self.endpoints]
        for e in self.endpoints:
            t = e.get_new_tasks()
            if (t is not None) and isinstance(t, (Task, list)) and t:
                debug("schedule_new_tasks", "Endpoint {} provided: {}", [e, t])
                self.schedule_task(t)

    def execute_task(self, t: Task):
        """Execute the given task

        Note that the task is pass in and can be provided on the fly rather
        than needing to be in the queue.
        """
        if t is None:
            debug("execute_task", "Tried to execute None")
            return

        task_result = []

        if self.profiler is None:

            for e in self.endpoints:
                r = e.task_handler(t)
                if r is not None:
                    task_result.append(r)

        else:
            timer = Timer()

            for e in self.endpoints:
                r = e.task_handler(t)
                if r is not None:
                    task_result.append(r)

            self.profiler.log_task(t.task_type, timer.end())

        debug("schedule_verbose",
              "Task execution resulted in {} new tasks",
              [len(list(task_result))])
        if task_result:
            # Only procede if not empty
            self.schedule_task(task_result)

    def set_terminate_flag(self):
        self.terminate_flag = True

        self.datastore.terminate()

        if self.profiler is not None:
            self.profiler.terminate()

    def terminate(self):
        """Execute actions needed to deconstruct a Node
        """
        debug("framework", "Node termianted")
        self.set_terminate_flag()

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
                debug("schedule_warning", "Cannot schedule None")
            elif isinstance(t, list):
                debug("schedule_empty_list", "Cannot schedule empty list")
            return

        if isinstance(t, list):
            # Recursively handle lists
            debug("schedule_verbose",
                  "Recursively scheduling list of {} tasks",
                  [len(t)])
            for item in t:
                debug("schedule_verbose",
                      "Recursively scheduling item {}",
                      [item])
                self.schedule_task(item)
            return

        if not isinstance(t, Task):
            # Handle non task objects
            debug("schedule_warning",
                  "Cannot schedule {} object {}", [type(t), t])
            return

        # Handle normal tasks
        debug("schedule_verbose", "Scheduling task {}", [t])
        if t.priority == TaskPriority.high:
            self.task_queue.append(t)  # High priotity at front (right)
        elif t.priority == TaskPriority.normal:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
            # TODO:  insert normal priority in between high and low
        elif t.priority == TaskPriority.low:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
        else:
            debug("schedule", "Cannot schedule task with priority: {}",
                  [t.priority])

    def get_next_task(self) -> Union[Task, None]:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            debug("schedule_event", "Ran out of tasks, getting more")
            self.get_new_tasks()
        debug(
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
