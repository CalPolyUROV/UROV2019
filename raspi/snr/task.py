""" Defines the basic unit of work for Nodes
"""

from enum import Enum
from typing import Callable, List, Union


class TaskType(Enum):
    debug_str = "debug_str"
    get_controls = "get_controls"
    process_controls = "process_controls"
    get_telemetry = "get_telemetry"
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

    The Task object is one that defines a action or event on the robot
    raspberry pi or the surface unit raspberry pi
    """

    def __init__(self, task_type: TaskType,
                 priority: TaskPriority,
                 val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.task_type == other.task_type) and
            (self.priority == other.priority) and
            (self.val_list == other.val_list)
        )

    def __repr__(self):
        return "Task: type: {}, priority: {}, val_list: {}".format(
            self.task_type, self.priority, self.val_list)


SomeTasks = Union[None, Task, List]
TaskHandler = Callable[[Task], SomeTasks]
TaskSource = Callable[[], SomeTasks]
TaskScheduler = Callable[[SomeTasks], None]
