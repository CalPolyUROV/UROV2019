"""The task class and associated code for using and passing tasks

The Task object is one that defines a action or event on the robot raspberry pi or the surface unit raspberry pi
"""

# System imports
from enum import IntEnum  # Used for task properties
import json

# Our imports
from utils import debug, debug_f
from controller import format_controls


class TaskType(IntEnum):
    debug_str = 0
    get_cntl = 1
    cntl_input = 2
    get_telemetry = 3
    serial_est_con = 4
    sockets_connect = 5
    blink_test = 6


class TaskPriority(IntEnum):
    high = 2
    normal = 1
    low = 0


class Task:
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
        debug_f("encode", "Encoding task as JSON bytes: {}", [self])
        data = (json.dumps(self, default=encode_task)).encode()
        debug_f("encode", "Encoded task as bytes: {}", [data])
        return data


def decode(data: bytes) -> Task:
    """Decoding method used in receiving of data over sockets
    """
    debug_f(
        "decode", "Trying to decode {}, which is {}", [data, data.__class__.__name__]
    )
    try:
        t = decode_task(json.loads(data.decode("utf-8")))
        debug_f("decode", "Decoded to {}, which is {}", [t, t.__class__.__name__])
        return t
    except:
        debug_f("decode", "Could not decode {}", [data])
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
    debug_f("decode", "JSON gave us {} which is {}",
            [dct, dct.__class__.__name__])
    if dct["__Task__"] == True:
        task_type = TaskType(dct["task_type"])
        priority = TaskPriority(dct["priority"])
        val_list = dct["val_list"]

        debug_f("decode", "\ttype: {}", [task_type])
        debug_f("decode", "\tpriority: {}", [priority])
        # debug_f("decode", "\tval_list: {}", val_list)

        return Task(task_type, priority, val_list)
    debug_f("decode", "Can't parse JSON from {}", [dct])
    return dct
