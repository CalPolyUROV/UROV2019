
from enum import Enum
from typing import Callable, List, Union


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


SomeTasks = Union[Task, List[Task], None]
Handler = Callable[[Task], SomeTasks]
TaskSource = Callable[[], SomeTasks]