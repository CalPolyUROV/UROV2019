from collections import deque
from time import time
from typing import Callable, List, Union

import _thread as thread
import settings
from snr.datastore import Datastore
from snr.factory import Factory
from snr.task import TaskHandler, SomeTasks, Task, TaskPriority, TaskSource
from snr.utils import Profiler, debug, sleep, print_exit


class Node:
    def __init__(self, mode: str, components: list):
        self.mode = mode
        self.task_queue = deque()
        self.data = Datastore()

        self.task_sources = []
        self.task_handlers = []
        self.endpoints = []

        self.profiler = None
        if settings.ENABLE_PROFILING:
            self.profiler = Profiler()

        self.terminate_flag = False  # Whether to exit main loop

        self.add_components(components)
        debug("framework",
              "Initialized with {} task sources,\
 {} task handlers,\
 {} endpoints",
              [len(self.task_sources),
               len(self.task_handlers),
               len(self.endpoints)])

    def add_components(self, new_components: List[Factory]):
        debug("framework_verbose", "Adding {} components",
              [len(new_components)])
        for c in new_components:
            source, handler, endpoint = c.get_task_callables(self.mode)

            if source is not None:
                self.task_sources.append(source)

            if handler is not None:
                self.task_handlers.append(handler)

            debug("framework_verbose", str(c))
            if endpoint is not None:
                self.endpoints.append(endpoint)

            debug("framework_verbose", "Component {} added {}, {}, {}",
                  [c, source, handler, endpoint])

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            debug("schedule_verbose", "Task queue: \n{}",
                  [self.repr_task_queue()])
        self.terminate()

    def schedule_new_tasks(self):
        """Retrieve tasks from constructor supplied source function
        Task or list of tasks are queued
        """
        new_tasks = []
        for s in self.task_sources:
            t = s()
            if t is Task:
                new_tasks.append(t)
            elif t is List[Task]:
                for _t in t:
                    new_tasks.append(_t)
        debug("schedule_verbose", "Scheduling new tasks {}", [new_tasks])
        self.schedule_task(new_tasks)

    def execute_task(self, t: Union[Task, None]):
        """Execute the given task

        The handler is provided at construction by the owner of the scheduler
        object.
        Note that the task is pass in and can be provided on the fly rather
        than needing to be in the queue.
        """
        if t is None:
            debug("execute_task", "Tried to execute None")
            return

        task_result = []

        if self.profiler is None:

            for h in self.task_handlers:
                task_result.append(h(t))

        else:
            start_time = time()

            for h in self.task_handlers:
                task_result.append(h(t))

            runtime = time() - start_time
            self.profiler.log_task(t.task_type, runtime)
            debug("task_profiling", "Ran {} task in {:6.3f} us",
                  [t.task_type, runtime * 1000000])

        if task_result is list:
            debug("schedule_verbose",
                  "Task execution resulted in {} new tasks",
                  [len(list(task_result))])
        self.schedule_task(task_result)

    def set_terminate_flag(self):
        self.terminate_flag = True

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
        if t is None:
            debug("schedule", "Cannot schedule None")
            return
        if type(t) is list:
            # Recursively handle lists
            debug("schedule_verbose",
                  "Recursively scheduling list of {} tasks", [len(t)])
            for item in t:
                debug("schedule_verbose", "Recursively scheduling {}", [item])
                self.schedule_task(item)
            return

        if type(t) is not Task:
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
            debug("schedule", "Cannot schedule task with priority: {}", [
                t.priority])

    def get_next_task(self) -> Union[Task, None]:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            debug("schedule_verbose", "Ran out of tasks, getting more")
            self.schedule_new_tasks()
        debug("schedule_verbose", "Popping task, {} remaining",
              [len(self.task_queue) - 1])
        return self.task_queue.pop()

    def store_data(self, key: str, data):
        self.data.store(key, data)

    def get_data(self, key: str):
        return self.data.get(key)

    def use_data(self, key: str):
        return self.data.use(key)

    def repr_task_queue(self) -> str:
        s = ""
        for t in self.task_queue:
            s = s + "\n\t" + str(t)
        return s
