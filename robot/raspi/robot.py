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
from task import SomeTasks, Task, TaskPriority, TaskType, decode
from utils import debug, debug_delay, exit, sleep  # Miscelaneous utilities


class Robot(Node):

    def __init__(self, mode: str):
        super().__init__(self.execute_task, self.get_new_tasks)

        self.database = Database()  # Handles all the robot's data

        self.schedule_task(self.initial_tasks())

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
            self.temp_mon = IntTempMon(
                "robot_pi_temperature", self.store_data)

    def execute_task(self, t: Task or None) -> SomeTasks:
        debug("execute_task", "Executing task: {} which is {}",
              [t, t.__class__.__name__])
        if t is None:
            return None
        sched_list = []

        # Debug string command
        if t.task_type == TaskType.debug_str:
            debug("execute_task", "Executing task: {}", t.val_list)

        # Process controls input
        elif t.task_type == TaskType.cntl_input:
            debug("robot_control", "Processing control input")
            debug("robot_control_verbose", "Control input {}", [t.val_list])
            sched_list.append(self.database.receive_controls(t.val_list))

        # Read sensor data
        elif t.task_type == TaskType.get_telemetry:
            debug("execute_task", "Executing task: {}", t.val_list)
            t = Task(TaskType.get_cntl, TaskPriority.high,
                     self.robot_data.telemetry_data())
            self.socket_connection.send_data(t.encode())

        # Initiate serial connection
        elif t.task_type == TaskType.serial_est_con:
            if settings.USE_SERIAL:
                sched_list.append(self.serial_connection.establish_contact())

        # Send serial data
        elif t.task_type == TaskType.serial_com:
            if settings.USE_SERIAL:
                data = t.val_list
                sched_list.append(
                    self.serial_connection.send_receive_packet(data))

        # Blink test
        elif t.task_type == TaskType.blink_test:
            if settings.USE_SERIAL:
                p = self.serial_connection.new_packet(
                    serial_coms.BLINK_CMD, t.val_list[0], t.val_list[1])
                self.serial_connection.send_receive_packet(p)

        # Terminate robot
        elif t.task_type == TaskType.terminate_robot:
            debug("robot_control",
                  "Robot {} program terminated by command", settings.ROBOT_NAME)
            self.terminate()

        else:  # Catch all
            debug("execute_task", "Unable to handle TaskType: {}", t.task_type)

        return sched_list

    def get_new_tasks(self) -> SomeTasks:
        """Task source function passed to Schedule constructor
        """
        sched_list = []

        if settings.USE_SOCKETS:
                # communicate over sockets to generate new tasks based on UI input
            # t = Task(TaskType.get_cntl, TaskPriority.high, [])
            t = self.socket_connection.request_data()
            debug("robot_verbose", "Got task {} from sockets connection", [t])
            sched_list.append(t)

        else:
            debug("robot", "Sockets disabled, queuing blink task")
            return Task(TaskType.blink_test, TaskPriority.high, [1, 1])

        if settings.USE_SERIAL:
            sched_list.append(
                Task(TaskType.get_telemetry, TaskPriority.normal, []))

        return sched_list

    def initial_tasks(self) -> list:
        """ Create a task to establish contact with the Arduino/Teensy

        These tasks will be executed in reverse order? shown here because high
        priority tasks are individually scheduled to the front of the queue
        (Please confirm this logic)
        """
        sched_list = []

        if settings.USE_SERIAL:
            sched_list.append(
                Task(TaskType.serial_est_con, TaskPriority.high, []))
        return sched_list

    def terminate(self) -> None:
        """Close the sockets connection
        """
        if settings.USE_SOCKETS:
            self.socket_connection.close_socket()

        if settings.USE_SERIAL:
            # Is terminating serial connection needed?
            pass

        super().set_terminate_flag()
