# Scheduling class for scheduling activities

from sockets_client import SocketsClient

class Schedule:
    def __init__(self):
        self.task_list = [] # Empty list
        self.socket_connection = SocketsClient() # Make sockets client obect

    def get_new_tasks(self):
        # communicate over sockets to generate new tasks based on UI input
        self.socket_connection.send_data("Give me tasks")
        pass

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
    
