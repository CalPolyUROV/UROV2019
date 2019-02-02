#!/usr/bin/python3.5
""" Code that runs on the Raspberry Pi inside the robot

This is the python program meant to run on the Raspberry Pi 3B+ located on
the robot. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

# Our imports
import settings  # Configuration file
import serial_coms
from robot_data import Database  # Stores data and preforms calculations
from serial_coms import SerialConnection  # Serial connection to Teensy
from snr import Node, Scheduler, Task, TaskPriority, TaskType, decode
# from spi_coms import SPIConnection  # Not yet implemented
from sockets_client import SocketsClient  # Sockets connection to topside
from utils import debug, exit, sleep, debug_delay  # Miscelaneous utilities


class Robot(Node):

    def __init__(self, mode: str):

        self.terminate_flag = False  # Whether to exit main loop
        self.database = Database()  # Handles all the robot's data

        # Make a schedule object
        self.scheduler = Scheduler(
            self.initial_tasks(), self.execute_task, self.get_new_tasks)

        # Create the serial_est_con connection object with the specified port
        if settings.USE_SERIAL:
            debug("serial", "Using serial as enabled in settings")
            self.serial_connection = SerialConnection()

        if mode.__eq__("debug"):
            settings.TOPSIDE_IP_ADDRESS = "localhost"

        if settings.USE_SOCKETS:
            debug("sockets", "Using sockets as enabled in settings")
            # Make sockets client object using our implementation
            self.socket_connection = SocketsClient(self.scheduler.schedule_task,
                                                   settings.TOPSIDE_IP_ADDRESS, 
                                                   settings.TOPSIDE_PORT
                                                   )

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            debug_delay()
        # self.terminate()

    def step_task(self):
        # Get the next task to execute
        t = self.scheduler.get_next_task()
        self.scheduler.execute_task(t)

    def execute_task(self, t: Task) -> None:
        sched_list = []

        # Debug string command
        if t.task_type == TaskType.debug_str:
            debug("execute_task", "Executing task: {}", t.val_list)
            return

        # Process controls input
        elif t.task_type == TaskType.cntl_input:
            debug("robot_control", "Processing control input")
            debug("robot_control_verbose", "Control input {}", [t.val_list])
            self.scheduler.schedule_task(self.database.receive_controls(t.val_list))
            return 

        # Read sensor data
        elif t.task_type == TaskType.get_telemetry:
            debug("execute_task", "Executing task: {}", t.val_list)
            t = Task(TaskType.get_cntl, TaskPriority.high,
                     self.robot_data.telemetry_data())
            self.socket_connection.send_data(t.encode())
            return 

        # Initiate serial connection
        elif t.task_type == TaskType.serial_est_con:
            if settings.USE_SERIAL:
                self.scheduler.schedule_task( self.serial_connection.establish_contact())
                return

        # Send serial data
        elif t.task_type == TaskType.serial_com:
            if settings.USE_SERIAL:
                data = t.val_list
                self.scheduler.schedule_task(self.serial_connection.send_receive_packet(data))
                return

        # Blink test
        elif t.task_type == TaskType.blink_test:
            p = self.serial_connection.new_packet(
                serial_coms.BLINK_CMD, t.val_list[0], t.val_list[1])
            self.serial_connection.send_receive_packet(p)
            return

        # Terminate robot
        elif t.task_type == TaskType.terminate_robot:
            debug("robot_control",
                  "Robot {} program terminated by command", settings.ROBOT_NAME)
            self.terminate = True  # RIP
            return

        else:  # Catch all
            debug("execute_task", "Unable to handle TaskType: {}", t.task_type)
            return 

    def get_new_tasks(self) -> Task or list:
        """Task source function passed to Schedule constructor
        """
        if not settings.USE_SOCKETS:
            debug("robot", "Sockets disabled, queuing blink task")
            return Task(TaskType.blink_test, TaskPriority.high, [1, 1])

        # communicate over sockets to generate new tasks based on UI input
        t = Task(TaskType.get_cntl, TaskPriority.high, [])
        data = self.socket_connection.transport_data(t.encode())
        return decode(data)

    def initial_tasks(self) -> list:
        """ Create a task to establish contact with the Arduino/Teensy

        These tasks will be executed in reverse order? shown here because high
        priority tasks are individually scheduled to the front of the queue
        (Please confirm this logic)
        """

        # This  initializes the sockets/networking code
        # Note: The sockets should not connect to the topside unit until after the
        #   serial connection has been made.
        #   (This is arbitrary, but the reasoning is that the robot should enumerate
        #   its own pieces prior to connecting to the server)
        #   (however the serial connection uses a handshake/"est_con")

        l = []
        # if settings.USE_SOCKETS:
        #     t = Task(TaskType.sockets_connect, TaskPriority.high, [])
        #     l.append(t)

        if settings.USE_SERIAL:
            t = Task(TaskType.serial_est_con, TaskPriority.high, [])
            l.append(t)
        return l

    def terminate(self) -> None:
        """Close the sockets connection
        """
        if settings.USE_SOCKETS:
            self.socket_connection.close_socket()
