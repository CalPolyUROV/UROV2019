""" SNR framework for scheduling and task management

Node: Task queue driven host for data and endpoints
AsyncEndpoint: Generate and process data for Nodes
Relay: Server data to other nodes
"""

from collections import deque
from time import time
from typing import Callable, Union

import _thread as thread
import settings
from snr_datastore import Datastore
from snr_task import Handler, SomeTasks, Task, TaskPriority, TaskSource
from snr_utils import Profiler, debug, sleep, u_exit


class Node:
    """Main thread object contianing task queue
    """

    def __init__(self, task_handler: Handler, task_source: TaskSource):
        self.task_queue = deque()
        self.data = Datastore()
        self.task_handler = task_handler
        self.task_source = task_source
        if settings.ENABLE_PROFILING:
            self.profiler = Profiler()
        else:
            self.profiler = None
        self.terminate_flag = False  # Whether to exit main loop

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            debug("schedule_verbose", "Task queue: \n{}",
                  [self.repr_task_queue()])
        self.terminate()

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

        if self.profiler is None:
            task_result = self.task_handler(t)
        else:
            start_time = time()
            task_result = self.task_handler(t)
            runtime = time() - start_time
            self.profiler.log_task(t.task_type, runtime)
            debug("task_profiling", "Ran {} task in {:6.3f} us",
                  [t.task_type, runtime * 1000000])

        if task_result is list:
            debug("schedule_verbose",
                  "Task execution resulted in {} new tasks",
                  [len(list(task_result))])
        self.schedule_task(task_result)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return len(self.task_queue) > 0

    def schedule_new_tasks(self):
        """Retrieve tasks from constructor supplied source function
        Task or list of tasks are queued
        """
        new_tasks = self.task_source()
        debug("schedule_verbose", "Scheduling new tasks {}", [new_tasks])
        self.schedule_task(new_tasks)

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


class AsyncEndpoint:
    """An Asynchronous endpoint of data for a node

    An AsyncEndpoint is part of a node, and runs in its own thread. An
    endpoint may produce data to be stored in the Node or retreive data from
    the Node. The endpoint has its loop handler function run according to its
    tick_rate (Hz).
    """

    def __init__(self, name: str, loop_handler: Callable,
                 tick_rate: float, profiler: Profiler):
        self.name = name
        self.loop_handler = loop_handler
        self.terminate_flag = False
        self.set_delay(tick_rate)
        self.profiler = profiler

    def set_delay(self, tick_rate: float):
        if tick_rate == 0:
            self.delay = 0.0
        else:
            self.delay = 1.0 / tick_rate

    def loop(self):
        debug("framework", "Starting async endpoint {} thread", [self.name])
        thread.start_new_thread(self.threaded_loop, ())

    def threaded_loop(self):
        while not self.terminate_flag:
            if self.profiler is None:
                self.loop_handler()
            else:
                start_time = time()
                self.loop_handler()
                runtime = time() - start_time
                self.profiler.log_task(self.name, runtime)
                debug("endpoint_profiling", "Ran {} task in {:6.3f} us",
                      [self.name, runtime * 1000000])

            self.tick()
        debug("framework", "Async endpoint {} exited loop", [self.name])
        u_exit("Endpoint thread exited by termination")

    def get_name(self):
        return self.name

    def tick(self):
        sleep(self.delay)
        # TODO: Ensure that this does not block other threads

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating endpoint {}", [self.name])

    def terminate(self):
        """Execute actions needed to destruct a AsyncEndpoint
        """
        raise NotImplementedError(
            "Subclass of endpoint does not implement terminate()")


class Relay:
    """An object belonging to a Node that connects it to other nodes or devices
    """

    def __init__(self, sub):
        self.sub = sub

    def request_data(self) -> SomeTasks:
        """The main event done by a Transport object
        """
        raise NotImplementedError(
            "Subclass of Transport does not implement send_and_receive()")

    def terminate(self):
        """Execute actions needed to destruct a Relay
        """
        raise NotImplementedError(
            "Subclass of Transport does not implement terminate()")
