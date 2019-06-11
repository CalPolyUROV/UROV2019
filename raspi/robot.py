""" Code that runs on the Raspberry Pi inside the robot

This is the python program meant to run on the Raspberry Pi 3B+ located on
the robot. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

import settings  # Configuration file
from internal_temp import IntTempMon
from robot_controls import ControlsProcessor
from serial_coms import SerialConnection  # Serial connection to Teensy
from snr_lib import Node
from snr_sockets_server import SocketsConfig, SocketsServer
from snr_task import SomeTasks, Task, TaskPriority, TaskType
from snr_utils import debug, debug_delay  # Miscelaneous utilities
from sockets_client import SocketsClient  # Sockets connection to topside


class Robot(Node):
    def __init__(self, mode: str):
        super().__init__(self.handle_task, self.get_new_tasks)
        self.mode = mode

        self.controls_processor = ControlsProcessor(self.store_throttle_data, self.profiler)

        self.serial_connection = SerialConnection()

        if settings.USE_CONTROLS_SOCKETS:
            debug("sockets", "Using sockets as enabled in settings")

            if self.mode.__eq__("debug"):
                debug("robot", "Running in debug mode: server IP is localhost")
                settings.CONTROLS_SOCKETS_CONFIG.ip = "localhost"
            # Make sockets client object using our implementation
            self.socket_connection = SocketsClient(settings.
                                                   CONTROLS_SOCKETS_CONFIG,
                                                   self.schedule_task)

        if settings.USE_TELEMETRY_SOCKETS:
            # Start sockets server endpoint
            if mode.__eq__("debug"):
                settings.TELEMETRY_SOCKETS_CONFIG.ip = "localhost"
            self.telemetry_server = SocketsServer(settings.TELEMETRY_SOCKETS_CONFIG,
                                                  self.serve_telemetry_data,
                                                  self.profiler)

        if settings.USE_ROBOT_PI_TEMP_MON:
            self.temp_mon = IntTempMon(settings.ROBOT_INT_TEMP_NAME,
                                       self.store_int_temp_data,
                                       self.profiler)

    def handle_task(self, t: Task) -> SomeTasks:
        debug("execute_task_verbose", "Executing task: {}", [t])

        sched_list = []

        # Get controls input
        if t.task_type == TaskType.get_controls:
            controller_data = self.socket_connection.request_data()
            t = Task(TaskType.process_controls, TaskPriority.high, [controller_data])
            debug("robot_verbose",
                  "Got task {} from controls sockets connection", [t])
            sched_list.append(t)
            pass

        # Process controls input
        elif t.task_type == TaskType.process_controls:
            debug("robot_control_event", "Processing control input")
            debug("robot_control_verbose", "Control input {}", [t.val_list])
            controls_data = t.val_list[0]
            new_task = self.controls_processor.receive_controls(controls_data)
            sched_list.append(new_task)

        # Read sensor data
        elif t.task_type == TaskType.get_telemetry:
            debug("execute_task", "Executing task: {}", [t.val_list])
            # TODO: Read sensor values from serial  and store in datastore

        # Send serial data
        elif t.task_type == TaskType.serial_com:
            debug("serial_verbose",
                  "Executing serial com task: {}", [t.val_list])
            result = self.serial_connection.send_receive(t.val_list[0],
                                                         t.val_list[1::])
            if result is None:
                debug("robot",
                      "Received no data in response from serial message")
            elif type(result) == Task:
                sched_list.append(result)
            elif type(result) == list:
                for new_task in list(result):
                    sched_list.append(new_task)

        # Blink test
        elif t.task_type == TaskType.blink_test:
            self.serial_connection.send_receive("blink", t.val_list)

        # Debug string command
        elif t.task_type == TaskType.debug_str:
            debug("execute_task", "Executing task: {}", t.val_list)

        # Terminate robot
        elif t.task_type == TaskType.terminate_robot:
            debug("robot_control",
                  "Robot {} program terminated by command",
                  settings.ROBOT_NAME)
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

        if settings.USE_CONTROLS_SOCKETS:
            t = Task(TaskType.get_controls, TaskPriority.high, [])
            sched_list.append(t)
        else:
            debug("robot", "Sockets disabled, queuing blink task")
            t = Task(TaskType.blink_test, TaskPriority.high, [1, 1])
            sched_list.append(t)

        t = Task(TaskType.get_telemetry, TaskPriority.normal, [])
        sched_list.append(t)

        return sched_list

    def terminate(self) -> None:
        """Close the sockets connection
        """
        if settings.USE_CONTROLS_SOCKETS:
            self.socket_connection.terminate()

        if settings.USE_TELEMETRY_SOCKETS:
            self.telemetry_server.terminate()

        self.serial_connection.terminate()

        self.set_terminate_flag()

    def store_throttle_data(self, throttle_data: dict):
        self.store_data(settings.THROTTLE_DATA_NAME, throttle_data)

    def serve_throttle_data(self):
        return self.get_data(settings.THROTTLE_DATA_NAME)

    def serve_telemetry_data(self)-> dict:
        telemetry_data = {}
        telemetry_data["throttle_data"] = self.serve_throttle_data()
        telemetry_data["motor_data"] = self.controls_processor.motor_control.motor_values
        telemetry_data["current_camera"] = self.controls_processor.cameras.current_camera
        telemetry_data["int_temp_data"] = self.get_data(settings.ROBOT_INT_TEMP_NAME)
        return telemetry_data

    def store_int_temp_data(self, int_temp: float):
        self.store_data(settings.ROBOT_INT_TEMP_NAME, int_temp)
