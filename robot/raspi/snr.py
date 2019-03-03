""" SNR framework for scheduling and task management

Scheduler
Node
Relay (aka Transport)
"""
# System imports
from typing import Callable, List, NewType, Union
from collections import deque
import _thread

# Our imports
import settings
from datastore import Datastore
from task import *
from utils import debug, exit, sleep


class Node:
    """ Implemented by an object which needs to have a queue of tasks that are executed
    """

    def __init__(self, task_handler: Handler, task_source: TaskSource):
        self.task_queue = deque()
        self.data = Datastore()
        self.task_handler = task_handler
        self.task_source = task_source

        self.terminate_flag = False  # Whether to exit main loop

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
        self.terminate()

    def set_terminate_flag(self):
        self.terminate_flag = True

    def terminate(self):
        """Execute actions needed to deconstruction an object that implements a Node
        """
        debug("framework", "Node termianted")
        self.terminate_flag = True

    def step_task(self):
        # Get the next task to execute
        t = self.get_next_task()
        self.execute_task(t)

    def schedule_task(self, t: SomeTasks):
        """ Adds a Task or the contents of a list of Tasks to a Scheduler's queue
        """
        if t is None:
            debug("schedule", "Cannot schedule None")
            return
        if isinstance(t, list):
            # Recursively handle lists
            debug("schedule", "Recursively scheduling list of tasks")
            for task in t:
                self.schedule_task(task)
            return
        elif not isinstance(t, Task):
            # Handle garbage
            debug("schedule", "Cannot schedule non task object {}", [t])
            return

        # Handle normal tasks
        debug("schedule", "Scheduling task {}", [t])
        if t.priority == TaskPriority.high:
            self.task_queue.append(t)  # High priotity at front (right)
        elif t.priority == TaskPriority.normal:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
            # TODO: intelligently insert normal priority tasks after any high priority tasks, but before low priority tasks
        elif t.priority == TaskPriority.low:
            self.task_queue.appendleft(t)  # Normal priotity at end (left)
        else:
            debug("schedule", "Cannot schedule task with priority: {}", [
                t.priority])

    def execute_task(self, t: Task or None) -> SomeTasks:
        """Execute the given task

        The handler is provided at construction by the owner of the scheduler object. 
        Note that the task is pass in and can be provided on the fly rather than needing to be in the queue. 
        """
        if t is None:
            debug("execute_task", "Tried to execute None")
            return
        task_result = self.task_handler(t)
        self.schedule_task(task_result)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return 0 < len(self.task_queue)

    def schedule_new_tasks(self):
        """Retrieve tasks from constructor supplied source function
        Task or list of tasks are queued
        """
        new_tasks = self.task_source()
        debug("framework", "Scheduling new tasks {}", [new_tasks])
        self.schedule_task(new_tasks)

    def get_next_task(self) -> Task or None:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            self.schedule_new_tasks()
        return self.task_queue.pop()

    def store_data(self, key: str, data):
        self.data.store(key, data)

    def get_data(self, key: str):
        return self.data.get(key)


class Source:
    """An Asynchronous source of data for a node

    A source is owned by a node, and runs a handler provided to it by the
    node. The handler stores the received data in the node's database and
    marks it as fresh. 
    """

    def __init__(self, name: str, loop_handler: Callable, tick_rate: int):
        self.name = name
        self.delay = 1.0 / tick_rate
        self.loop_handler = loop_handler
        self.terminate_flag = False

    def loop(self):
        debug("framework", "Starting source {} thread", [self.name])
        _thread.start_new_thread(self.threaded_loop, ())

    def threaded_loop(self):
        while not self.terminate_flag:
            self.loop_handler()
            self.tick()
        debug("framework", "Source {} ending loop", [self.name])
        exit("Source thread exited by termination")

    def get_name(self):
        return self.name

    def tick(self):
        sleep(self.delay)
        # TODO: Ensure that this does not block other threads

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating source {}", [self.name])

    def terminate(self):
        """Execute actions needed to deconstruction an object that implements a Transport
        """
        raise NotImplementedError(
            "Subclass of Source does not implement terminate()")


class Server:
    """An Asynchronous accessor of data for another node
    """

    def __init__(self, name: str, loop_handler: Callable):
        self.name = name
        self.loop_handler = loop_handler
        self.terminate_flag = False

    def loop(self):
        debug("framework", "Starting server thread: {}", [self.name])
        _thread.start_new_thread(self.threaded_loop, ())

    def threaded_loop(self):
        while not self.terminate_flag:
            self.loop_handler()
        debug("framework", "Server {} ending loop", [self.name])
        exit("Server thread exited by termination")
        # TODO: Kill just this thread, maybe through join()?

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating server: {}", [self.name])

    def terminate(self):
        """Execute actions needed to deconstruction an object that implements a Transport
        """
        raise NotImplementedError(
            "Subclass of Server does not implement terminate()")


class Relay:
    """An object belonging to a Node that connects it to other nodes or devices
    """

    def __init__(self, request_data: Callable):
        self.request_data = request_data

    def request_data(self, data) -> SomeTasks:
        """The main event done by a Transport object
        """
        raise NotImplementedError(
            "Subclass of Transport does not implement send_and_receive()")

    def terminate(self):
        """Execute actions needed to deconstruction an object that implements a Transport
        """
        raise NotImplementedError(
            "Subclass of Transport does not implement terminate()")
