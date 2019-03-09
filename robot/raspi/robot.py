""" Code that runs on the Raspberry Pi inside the robot

This is the python program meant to run on the Raspberry Pi 3B+ located on
the robot. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

import serial_coms
import settings  # Configuration file
from internal_temp import IntTempMon
from robot_data import Database  # Stores data and preforms calculations
from serial_coms import SerialConnection  # Serial connection to Teensy
from snr import Node
from sockets_client import SocketsClient  # Sockets connection to topside
from task import *
from utils import debug, exit, sleep, debug_delay  # Miscelaneous utilities


class Robot(Node):

    def __init__(self, mode: str):
        super().__init__(self.handle_task, self.get_new_tasks)
        self.mode = mode

        self.database = Database()  # Handles all the robot's data

        # Create the serial_est_con connection object with the specified port
        if settings.USE_SERIAL:
            debug("serial", "Using serial as enabled in settings")
            self.serial_connection = SerialConnection()

        if mode.__eq__("debug"):
            settings.TOPSIDE_IP_ADDRESS = "localhost"

        if settings.USE_SOCKETS:
            debug("sockets", "Using sockets as enabled in settings")
            # Make sockets client object using our implementation
            self.socket_connection = SocketsClient(self.schedule_task,
                                                   (settings.TOPSIDE_IP_ADDRESS,
                                                    settings.TOPSIDE_PORT)
                                                   )
        if settings.USE_ROBOT_PI_TEMP_MON:
            self.temp_mon = IntTempMon(settings.ROBOT_INT_TEMP_NAME,
                                       self.store_temperature_data)

    def handle_task(self, t: Task or None) -> SomeTasks:
        debug("execute_task_verbose", "Executing task: {}", [t])

        sched_list = []

        # Get controls input
        if t.task_type == TaskType.get_cntl:
            # t = self.socket_connection.request_data()
            # debug("robot_verbose", "Got task {} from sockets connection", [t])
            # sched_list.append(t)
            pass

        # Process controls input
        elif t.task_type == TaskType.cntl_input:
            debug("robot_control", "Processing control input")
            debug("robot_control_verbose", "Control input {}", [t.val_list])
            sched_list = self.database.receive_controls(t.val_list)

        # Read sensor data
        elif t.task_type == TaskType.get_telemetry:
            debug("execute_task", "Executing task: {}", [t.val_list])
            # TODO: Read sensor values by serial connection and store in datastore

        # Send serial data
        elif t.task_type == TaskType.serial_com:
            debug("serial", "Executing serial com task: {}", [t.val_list])
            t = self.serial_connection.send_receive(
                t.val_list[0], t.val_list[1::])
            sched_list = append_task(t, sched_list)

        # Blink test
        elif t.task_type == TaskType.blink_test:
            self.serial_connection.send_receive("blink", t.val_list)

        # Debug string command
        elif t.task_type == TaskType.debug_str:
            debug("execute_task", "Executing task: {}", t.val_list)

        # Terminate robot
        elif t.task_type == TaskType.terminate_robot:
            debug("robot_control",
                  "Robot {} program terminated by command", settings.ROBOT_NAME)
            self.terminate()

        else:  # Catch all
            debug("execute_task", "Unable to handle TaskType: {}", t.task_type)

        if self.mode.__eq__("debug"):
            debug_delay()
        return sched_list

    def get_new_tasks(self) -> SomeTasks:
        """Task source function passed to Schedule constructor
        """
        sched_list = []

        if settings.USE_SOCKETS:
            # t = Task(TaskType.get_cntl, TaskPriority.low, [])

            t = self.socket_connection.request_data()
            debug("robot_verbose", "Got task {} from sockets connection", [t])
            sched_list.append(t)

        else:
            debug("robot", "Sockets disabled, queuing blink task")
            t = Task(TaskType.blink_test, TaskPriority.high, [1, 1])
            sched_list.append(t)

        if settings.USE_SERIAL:
            t = Task(TaskType.get_telemetry, TaskPriority.normal, [])
            # sched_list.append(t)

        return sched_list

    def terminate(self) -> None:
        """Close the sockets connection
        """
        if settings.USE_SOCKETS:
            self.socket_connection.terminate()

        if settings.USE_SERIAL:
            self.serial_connection.terminate()
            pass

        self.set_terminate_flag()

    def store_int_temp_data(self, int_temp: float):
        self.store_data(settings.ROBOT_INT_TEMP_NAME, int_temp)
