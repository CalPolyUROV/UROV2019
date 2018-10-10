# Scheduling class for scheduling activities

from enum import Enum

# Serial imports
from serial_coms import find_port
from serial_coms import SerialConnection
from serial_coms import Packet

# Sockets networking import
from sockets_client import SocketsClient


class TaskType(Enum):
    debug_str = 0
    cntl_input = 1
    get_telemetry = 2
    serial_est_con = 3

class TaskPriority(Enum):
    high = 1
    normal = 0

class Task:
    def __init__(self, task_type: TaskType, priority: TaskPriority, val_list: list):
        self.task_type = task_type
        self.priority = priority
        self.val_list = val_list

class Schedule:
    def __init__(self):
        self.task_list = [] # Empty list
        self.task_index = 0  
        self.serial_connection = SerialConnection() # Create the serial_est_con connection object with the specified port  
        self.socket_connection = SocketsClient("localhost", 9120) # Make sockets client obect

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

    def execute_task(self, t: Task):
        # TODO: Send commands to Teensy (In final commands will come from sockets connection OR event loop will get updated values in an RTOS manner)
        # TODO: Write logic choosing a command to send (maybe use a queue)

        if (t.task_type == TaskType.debug_str):
            print("Executing task: {}".format(t.val_list))
        elif (t.task_type == TaskType.cntl_input):
            print("Executing task: {}".format(t.val_list))
        elif (t.task_type == TaskType.get_telemetry):
            print("Executing task: {}".format(t.val_list))
        elif (t.task_type == TaskType.serial_est_con):
            self.serial_connection.establish_contact()
        else:
            print("Unable to handle TaskType: {}".format(t.task_type))

    # Report whether there are enough tasks left in the queue
    def has_tasks(self):
        return len(self.task_list) 

    # take the next task off the queue 
    def get_next_task(self):
        return self.task_list.pop(0)

    def terminate(self):
        self.socket_connection.close_socket() 
    