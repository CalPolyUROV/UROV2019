# """ Code that runs on the Raspberry Pi inside the robot

# This is the python program meant to run on the Raspberry Pi 3B+ located on
# the robot. This program acts as a intermediary between the Raspberry Pi on
# the surface unit and the Arduino/Teensy on the robot. The scheduling module
# used in this program manages the serial and sockets connections to the
# Arduino/Teensy and topside raspberry Pi respectively.
# """

# import settings
# from internal_temp import IntTempMon
# from robot_controls import ControlsProcessor
# from snr.comms.serial.serial_coms import SerialConnection
# from snr.comms.sockets.client import SocketsClient
# from snr.comms.sockets.server import SocketsServer
# from snr.node import Node
# from snr.task import SomeTasks, Task, TaskPriority, TaskType
# from snr.utils import debug, debug_delay


# class Robot(Node):
#     def __init__(self, mode: str):
#         super().__init__(self.handle_task, self.get_new_tasks)
#         self.mode = mode

#         self.controls_processor = ControlsProcessor(self.profiler)

#         if settings.USE_CONTROLS_SOCKETS:
#             debug("sockets", "Using sockets as enabled in settings")

#             if self.mode.__eq__("debug"):
#                 debug("robot", "Running in debug mode: server IP is localhost")
#                 settings.CONTROLS_SOCKETS_CONFIG.ip = "localhost"
#             # Make sockets client object using our implementation
#             self.socket_connection = SocketsClient(
#                 settings.CONTROLS_SOCKETS_CONFIG,
#                 self.schedule_task)

#         if settings.USE_TELEMETRY_SOCKETS:
#             # Start sockets server endpoint
#             if mode.__eq__("debug"):
#                 settings.TELEMETRY_SOCKETS_CONFIG.ip = "localhost"
#             self.telemetry_server = SocketsServer(
#                 settings.TELEMETRY_SOCKETS_CONFIG,
#                 self.serve_telemetry_data,
#                 self.profiler)

#         if settings.USE_ROBOT_PI_TEMP_MON:
#             self.temp_mon = IntTempMon(
#                 settings.ROBOT_INT_TEMP_NAME,
#                 self.store_int_temp_data,
#                 self.profiler)

#     def handle_task(self, t: Task) -> SomeTasks:
#         debug("execute_task_verbose", "Executing task: {}", [t])

#         sched_list = []

#         # Read sensor data
#         if t.task_type == TaskType.get_telemetry:
#             debug("execute_task", "Executing task: {}", [t.val_list])
#             # TODO: Read sensor values from serial  and store in datastore

#             data = {}
#             data["throttle_data"] = self.controls_processor.throttle
#             data["motor_data"] = self.controls_processor.motor_control.\
#                 motor_values
#             data["current_camera"] = self.controls_processor.cameras.\
#                 current_camera
#             data["int_temp_data"] = self.get_data(settings.ROBOT_INT_TEMP_NAME)
#             self.store_data(settings.TELEMETRY_DATA_NAME, data)

#         # Send serial data

#         # Debug string command
#         elif t.task_type == TaskType.debug_str:
#             debug("execute_task", "Executing task: {}", t.val_list)

#         # Terminate robot
#         elif t.task_type == TaskType.terminate_robot:
#             debug("robot_control",
#                   "Robot {} program terminated by command",
#                   settings.ROBOT_NAME)
#             self.terminate()

#         else:  # Catch all
#             debug("execute_task", "Unable to handle TaskType: {}", t.task_type)

#         if self.mode.__eq__("debug"):
#             debug_delay()
#         return sched_list

#     def get_new_tasks(self) -> SomeTasks:
#         """Task source function passed to Schedule constructor
#         """
#         sched_list = []

#         if settings.USE_CONTROLS_SOCKETS:
#             t = Task(TaskType.get_controls, TaskPriority.high, [])
#             sched_list.append(t)
#         else:
#             debug("robot", "Sockets disabled, queuing blink task")
#             t = Task(TaskType.blink_test, TaskPriority.high, [1, 1])
#             sched_list.append(t)

#         t = Task(TaskType.get_telemetry, TaskPriority.normal, [])
#         sched_list.append(t)

#         return sched_list

#     def terminate(self) -> None:
#         """Close the sockets connection
#         """
#         if settings.USE_CONTROLS_SOCKETS:
#             self.socket_connection.terminate()

#         if settings.USE_TELEMETRY_SOCKETS:
#             self.telemetry_server.terminate()

#         self.serial_connection.terminate()

#         self.set_terminate_flag()

#     def store_throttle_data(self, throttle_data: dict):
#         self.store_data(settings.THROTTLE_DATA_NAME, throttle_data)

#     def serve_throttle_data(self):
#         return self.get_data(settings.THROTTLE_DATA_NAME)

#     def serve_telemetry_data(self) -> dict:
#         return self.get_data(settings.TELEMETRY_DATA_NAME)

#     def store_int_temp_data(self, int_temp: float):
#         self.store_data(settings.ROBOT_INT_TEMP_NAME, int_temp)
