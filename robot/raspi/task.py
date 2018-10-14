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

