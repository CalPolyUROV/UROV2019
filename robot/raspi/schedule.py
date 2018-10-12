# Scheduling class for scheduling activities

# System imports
from enum import Enum  # Used for task properties

import settings
from debug import debug  # Debug printing and logging
from debug import debug_f

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
    sockets_connect = 4


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
        self.task_list = []  # Empty list
        self.task_index = 0
        # Create the serial_est_con connection object with the specified port
        self.serial_connection = SerialConnection()
        self.socket_connection = SocketsClient(
            "localhost", 9120)  # Make sockets client obect

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

    def schedule_initial_tasks(self):
        """ Create a task to establish contact with the Arduino/Teensy
        """
        if(settings.USE_SOCKETS):
            task_sockets_connect = Task(TaskType.sockets_connect,
                                        TaskPriority.high,
                                        [])
            self.schedule_task(task_sockets_connect)

        if(settings.USE_SERIAL):
            task_serial_est_con = Task(TaskType.serial_est_con,
                                       TaskPriority.high,
                                       [])
            self.schedule_task(task_serial_est_con)

    def execute_task(self, t: Task):
        # TODO: Send commands to Teensy (In final commands will come from sockets connection OR event loop will get updated values in an RTOS manner)
        # TODO: Write logic choosing a command to send (maybe use a queue)

        if (t.task_type == TaskType.debug_str):
            debug_f("execute_task", "Executing task: {}", t.val_list)

        elif (t.task_type == TaskType.cntl_input):
            debug_f("execute_task", "Executing task: {}", t.val_list)

        elif (t.task_type == TaskType.get_telemetry):
            debug_f("execute_task", "Executing task: {}", t.val_list)

        elif (t.task_type == TaskType.serial_est_con):
            self.serial_connection.establish_contact()

        elif (t.task_type == TaskType.sockets_connect):
            self.socket_connection.connect_server()

        else:
            debug_f("execute_task", "Unable to handle TaskType: {}", t.task_type)

    def has_tasks(self):
        """Report whether there are enough tasks left in the queue
        """
        return len(self.task_list)

    def get_next_task(self):
        """Take the next task off the queue
        """
        return self.task_list.pop(0)

    def terminate(self):
        self.socket_connection.close_socket()
