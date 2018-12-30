""" SNR framework for scheduling and task management

Implement a Node class that contains a Schedule object. 
"""

# Our imports
import settings
from enum import IntEnum  # Used for task properties
import json
from typing import Union

# Our imports
from utils import debug
from controller import format_controls


class Node:
    """ Implemented by an object which needs to have a queue of tasks that are executed 
    """

    def __init__(self):
        raise NotImplementedError(
            "Subclass of Node does not implement __init__()")

    def loop(self):
        """The main event loop for a Node object
        """
        raise NotImplementedError("Subclass of Node does not implement loop()")

    def terminate(self):
        """Execute actions needed to deconstruction an object that implements a Node
        """
        raise NotImplementedError(
            "Subclass of Node does not implement terminate()")


class TaskType(IntEnum):
    debug_str = 0
    get_cntl = 1
    cntl_input = 2
    get_telemetry = 3
    serial_est_con = 4
    sockets_connect = 5
    blink_test = 6
    terminate_robot = 7


class TaskPriority(IntEnum):
    high = 2
    normal = 1
    low = 0


class Task:
    """The task class and associated code for using and passing tasks

    The Task object is one that defines a action or event on the robot raspberry pi or the surface unit raspberry pi
    """

    def __init__(self, task_type: TaskType, priority: TaskPriority, val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__)
            and (self.task_type == other.task_type)
            and (self.priority == other.priority)
            and (self.val_list == other.val_list)
        )

    def __repr__(self):
        if self.task_type == TaskType.cntl_input:
            return "Task: type: {}, priority: {}, val_list: {}".format(
                self.task_type, self.priority, format_controls(self.val_list)
            )
        return "Task: type: {}, priority: {}, val_list: {}".format(
            self.task_type, self.priority, self.val_list
        )

    def encode(self) -> bytes:
        """Encoding method used in sending data over sockets
        """
        debug("encode", "Encoding task as JSON bytes: {}", [self])
        data = (json.dumps(self, default=encode_task)).encode()
        debug("encode", "Encoded task as bytes: {}", [data])
        return data


def decode(data: bytes) -> Task:
    """Decoding method used in receiving of data over sockets
    """
    debug(
        "decode", "Trying to decode {}, which is {}", [
            data, data.__class__.__name__]
    )
    try:
        t = decode_task(json.loads(data.decode("utf-8")))
        debug("decode", "Decoded to {}, which is {}",
              [t, t.__class__.__name__])
        return t
    except:
        debug("decode", "Could not decode {}", [data])
        return None


def encode_task(t: Task):
    """Encoding method passed to json.dumps()
    """
    if isinstance(t, Task):
        dct = {}
        dct["__Task__"] = True
        dct["task_type"] = t.task_type
        dct["priority"] = t.priority
        dct["val_list"] = t.val_list
        return dct
    type_name = t.__class__
    raise TypeError("Object of type '{}' is not a Task".format(type_name))


def decode_task(dct: dict) -> Task:
    """Decoding function that receives a dict from json.loads()
    """
    debug("decode_verbose", "JSON gave us {} which is {}",
            [dct, dct.__class__.__name__])
    if dct["__Task__"] == True:
        task_type = TaskType(dct["task_type"])
        priority = TaskPriority(dct["priority"])
        val_list = dct["val_list"]

        debug("decode_verbose", "\ttype: {}\n\tpriority: {}", [task_type, priority])
        # debug("decode", "\tval_list: {}", val_list)

        return Task(task_type, priority, val_list)
    debug("decode", "Can't parse JSON from {}", [dct])
    return dct


class ComsCon:
    pass


class Schedule:
    """ Manages a queue of tasks for a Node object

    A Node object should create a Schedule object and then 
    step through (step_task()) or loop()

    """

    def __init__(self, initial_tasks: list, handler, task_source):
        self.task_queue = initial_tasks
        # self.task_index = 0
        self.handler = handler
        self.task_source = task_source

    def schedule_task(self, input: Union[Task, list]):
        """
        """
        if isinstance(input, list):
            for t in input:
                self.schedule_task(t)
        elif not isinstance(input, Task):
            debug("schedule", "Cannot schedule non task object {}", [input])
            return
        debug("schedule", "Scheduling task {}", [input])

        if input.priority == TaskPriority.high:
            self.task_queue.insert(0, input)  # High priotity at front
        elif input.priority == TaskPriority.normal:
            self.task_queue.append(input)  # Normal priotity at end
            # TODO: intelligently insert normal priority tasks after any high priority tasks, but before low priority tasks
        elif input.priority == TaskPriority.low:
            self.task_queue.append(input)  # Normal priotity at end
        else:
            debug("schedule", "Cannot schedule task with priority: {}", [
                    input.priority])
        # self.task_index += 1

    def execute_task(self, t: Task):
        """Execute the given task

        The handler is provided at construction by the owner of the scheduler object. 
        Note that the task is pass in and can be provided on the fly rather than needing to be in the queue. 
        """
        if t == None:
            debug("execute_task", "Tried to execute None")
            return
        # TODO: Send commands to Teensy (In final commands will come from sockets connection OR event loop will get updated values in an RTOS manner)
        # TODO: Write logic choosing a command to send (maybe use a queue)
        sched_list = self.handler(t)
        if not (sched_list == None):
            for t in sched_list:
                self.schedule_task(t)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return 0 < len(self.task_queue)

    def get_new_tasks(self) -> bool:
        """Retrieve tasks from constructor supplied source function
        Task or list of tasks are queued
        """
        sched_list = self.task_source()
        self.schedule_task(sched_list)

    def get_next_task(self) -> Task or None:
        """Take the next task off the queue
        """
        if not self.has_tasks():
            if not self.get_new_tasks():
                # TODO: possibly call get_new_tasks()
                return None

        return self.task_queue.pop(0)
