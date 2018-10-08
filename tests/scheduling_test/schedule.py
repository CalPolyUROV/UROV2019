# Scheduling class for scheduling activities

from enum import Enum

from sockets_client import SocketsClient

class TaskType(Enum):
    debug_str = 0

class TaskPriority(Enum):
    high = 1
    normal = 0

class Schedule:
    def __init__(self):
        self.task_list = [] # Empty list
        self.socket_connection = SocketsClient("localhost", 9120) # Make sockets client obect
        self.task_index = 0

    def get_new_tasks(self):
        # communicate over sockets to generate new tasks based on UI input
        data = self.socket_connection.send_data("Give me tasks")
        self.schedule_task(Task(TaskType.debug_str,
                                TaskPriority.normal, 
                                ["debug_str", self.task_index, data]))
        return

    def schedule_task(self, task):
        if(task.priority == TaskPriority.high):
            self.task_list.insert(0, task)
        else:
            self.task_list.append(task)
        self.task_index += 1    

    # Report whether there are enough tasks left in the queue
    def has_tasks(self):
        return len(self.task_list) 

    # take the next task off the queue 
    def get_next_task(self):
        return self.task_list.pop(0)

class Task:
    def __init__(self, task_type: TaskType, priority: TaskPriority, val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

    def execute_task(self):
        if (self.task_type == TaskType.debug_str):
            print(self.val_list)
        else:
            print("Unable to handle TaskType: {}".format(self.task_type))
    
