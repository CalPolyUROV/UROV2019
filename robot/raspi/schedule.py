# Scheduling class for scheduling activities

# Our imports
import settings
from task import Task
from task import TaskType
from task import TaskPriority
from task import decode as decode_task
from debug import debug  # Debug printing and logging
from debug import debug_f

# Serial imports
from serial_coms import find_port
from serial_coms import SerialConnection
from serial_coms import Packet

# Sockets networking import
from sockets_client import SocketsClient


class Schedule:
    def __init__(self):
        self.task_list = []  # Empty list
        self.task_index = 0
        # Create the serial_est_con connection object with the specified port
        if(settings.USE_SERIAL):
            debug("schedule", "Using serial as enabled in settings")
            self.serial_connection = SerialConnection()
        if(settings.USE_SOCKETS):
            debug("schedule", "Using sockets as enabled in settings")
            self.socket_connection = SocketsClient(
                "localhost", 9120)  # Make sockets client obect

    def schedule_task(self, t: Task):
        if(t.priority == TaskPriority.high):
            self.task_list.insert(0, t)
        elif(TaskPriority == TaskPriority.normal):
            self.task_list.append(t)
            # TODO: intelligently insert normal priority tasks after any high priority tasks, but before low priority tasks
        elif(TaskPriority == TaskPriority.low):
            self.task_list.append(t)
        else:
            debug_f(
                "schedule", "Cannot schedule task with unknown priority: {}", [t.priority])
        self.task_index += 1

    def schedule_initial_tasks(self):
        """ Create a task to establish contact with the Arduino/Teensy

        These tasks will be executed in reverse order shown here because high
        priority tasks are inidividually schedule to the front of the queue
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
            if(settings.USE_SERIAL):
                self.serial_connection.establish_contact()

        elif (t.task_type == TaskType.sockets_connect):
            self.socket_connection.connect_server()

        else:
            debug_f("execute_task", "Unable to handle TaskType: {}", t.task_type)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return 0 < len(self.task_list)

    def get_new_tasks(self) -> None:
        # communicate over sockets to generate new tasks based on UI input
        t: Task = Task(TaskType.get_cntl, TaskPriority.high,
                       ["control input pls"])
        data: bytes = self.socket_connection.send_data(t.encode())
        self.schedule_task(decode_task(data))
        return

    def get_next_task(self):
        """Take the next task off the queue
        """
        if (not self.has_tasks()):
            self.get_new_tasks()
        return self.task_list.pop(0)

    def terminate(self):
        self.socket_connection.close_socket()
