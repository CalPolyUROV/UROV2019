"""The task class and associated code for using and passing tasks
"""

# System imports
from enum import IntEnum  # Used for task properties
import json


class TaskType(IntEnum):
    debug_str = 0
    cntl_input = 1
    get_telemetry = 2
    serial_est_con = 3
    sockets_connect = 4


class TaskPriority(IntEnum):
    high = 1
    normal = 0


class Task:
    def __init__(self, task_type: TaskType, priority: TaskPriority, val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

    def encode(self):
        return json.dumps(self, default=encode_task)


def decode(data):
    return json.loads(data, object_hook=decode_task)


def encode_task(t: Task):
    if isinstance(t, Task):
        return (t.task_type, t.priority, t.val_list)
    else:
        type_name = t.__class__.__name__
        raise TypeError(
            f"Object of type '{type_name}' is not JSON serializable")


def decode_task(dictionary):
    if "__Task__" in dictionary:
        return Task(dictionary["task_type"], dictionary["priority"], dictionary["val_list"])
    return dictionary
