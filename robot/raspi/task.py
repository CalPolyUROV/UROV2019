
from enum import Enum
from typing import NewType, Callable, List, Union
import json

from utils import debug


class TaskType(Enum):
    debug_str = "debug_str"
    get_cntl = "get_cntl"
    cntl_input = "cntl_input"
    get_telemetry = "get_telemetry"
    serial_est_con = "serial_est_con"
    serial_com = "serial_com"
    blink_test = "blink_test"
    update_ui = "update_ui"
    terminate_robot = "terminate_robot"


class TaskPriority(Enum):
    high = 3
    normal = 2
    low = 1


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
                self.task_type, self.priority, self.val_list)
        return "Task: type: {}, priority: {}, val_list: {}".format(
            self.task_type, self.priority, self.val_list
        )

    # def encode(self) -> bytes:
    #     """Encoding method used in sending data over sockets
    #     """
    #     debug("encode", "Encoding task: {}", [self])
    #     data = (json.dumps(self, default=encode_task)).encode()
    #     debug("encode_verbose", "Encoded task as JSON bytes: {}", [data])
    #     return data


SomeTasks = NewType("SomeTasks", Union[Task, List[Task], None])
Handler = NewType("Handler", Callable[[Task], SomeTasks])
TaskSource = NewType("TaskSource", Callable[[], SomeTasks])


# def decode(data: bytes) -> Task:
#     """Decoding method used in receiving of data over sockets
#     """
#     debug(
#         "decode", "Trying to decode {}, which is {}", [
#             data, data.__class__.__name__]
#     )
#     try:
#         t = decode_task(json.loads(data.decode("utf-8")))
#         debug("decode", "Decoded to {}, which is {}",
#               [t, t.__class__.__name__])
#         return t
#     except:
#         debug("decode", "Could not decode {}", [data])
#     return None


# def decode_task(dct: dict) -> Task:
#     """Decoding function that receives a dict from json.loads()
#     """
#     debug("decode_verbose", "JSON gave us {} {}",
#           [dct.__class__.__name__, dct])
#     if dct["__Task__"] == True:
#         task_type = TaskType(dct["task_type"])
#         priority = TaskPriority(dct["priority"])
#         val_list = dct["val_list"]

#         debug("decode_verbose", "type: {}\tpriority: {}",
#               [task_type, priority])
#         # debug("decode", "\tval_list: {}", val_list)

#         return Task(task_type, priority, val_list)
#     debug("decode", "Can't parse JSON from {}", [dct])
#     return dct


# def encode_task(t: Task):
#     """Encoding method passed to json.dumps()
#     """
#     if isinstance(t, Task):
#         dct = {}
#         dct["__Task__"] = True
#         dct["task_type"] = t.task_type
#         dct["priority"] = t.priority
#         dct["val_list"] = t.val_list
#         return dct
#     type_name = t.__class__
#     raise TypeError("Object of type '{}' is not a Task".format(type_name))
