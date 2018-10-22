"""The task class and associated code for using and passing tasks
"""

# System imports
from enum import IntEnum  # Used for task properties
import json

# Our imports
from debug import debug_f


class TaskType(IntEnum):
    debug_str = 0
    get_cntl = 1
    cntl_input = 2
    get_telemetry = 3
    serial_est_con = 4
    sockets_connect = 5


class TaskPriority(IntEnum):
    high = 2
    normal = 1
    low = 0


class Task:
    def __init__(self, task_type: TaskType, priority: TaskPriority, val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

    def encode(self) -> bytes:
        return json.dumps(self, default=encode_task).encode()


def decode(data):
    return json.loads(data, object_hook=decode_task)


def encode_task(t: Task):
    if isinstance(t, Task):
        return ("__Task__", t.task_type, t.priority, t.val_list)
    else:
        type_name = t.__class__.__name__
        raise TypeError("Object of type '{}' is not a Task".format(type_name))


def decode_task(dictionary):
    if "__Task__" in dictionary:
        return Task(dictionary["task_type"], dictionary["priority"], dictionary["val_list"])
    return dictionary
