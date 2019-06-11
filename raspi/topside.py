""" SNR Node that runs on the surface unit

Called by main
"""

import settings
from snr_controller import Controller
from snr_lib import Node
from snr_sockets_server import SocketsServer
from snr_task import SomeTasks, Task, TaskPriority, TaskType
from snr_utils import debug, sleep
from sockets_client import SocketsClient
from topside_clui import TopsideClui


class Topside(Node):
    """Node for surface unit

    Implements an Node to use Sockets and a PyGame joystick to send
    control data to robot and show telemetry data from robot
    """

    def __init__(self, mode: str):
        super().__init__(self.handle_task, self.get_new_tasks)

        # TODO: Remotely start robot program from topside

        # Start sockets server endpoint
        if settings.USE_CONTROLS_SOCKETS:
            if mode.__eq__("debug"):
                settings.CONTROLS_SOCKETS_CONFIG.ip = "localhost"
            self.controls_sockets_server = SocketsServer(
                settings.CONTROLS_SOCKETS_CONFIG,
                self.serve_controller_data,
                self.profiler)

        if settings.USE_TELEMETRY_SOCKETS:
            if mode.__eq__("debug"):
                settings.TELEMETRY_SOCKETS_CONFIG.ip = "localhost"
            self.telemetry_sockets_client = SocketsClient(
                settings.TELEMETRY_SOCKETS_CONFIG,
                self.store_telemetry_data)

        # Start XBox controller endpoint
        self.xbox_controller = Controller(settings.CONTROLLER_NAME,
                                          self.store_controller_data,
                                          self.profiler)

        # Start CLUI endpoint
        self.ui = TopsideClui(settings.TOPSIDE_CLUI_NAME, self.fetch_ui_data)

        debug("framework", "Topside Node created")

    def handle_task(self, t: Task) -> SomeTasks:
        debug("execute_task_verbose", "Executing task: {} ", [t])
        sched_list = []

        if (t.task_type == TaskType.debug_str):
            debug("execute_task", "Debug_str task: {}", [t.val_list])

        elif (t.task_type == TaskType.get_telemetry):
            telemetry_data = self.telemetry_sockets_client.request_data()
            debug("telemetry_verbose", "Recieved data: {}", [telemetry_data])
            self.store_telemetry_data(telemetry_data)

        else:
            debug("execute_task",
                  "Unable to handle TaskType: {}, values: {}",
                  [t.task_type, t.val_list])

        return sched_list

    def get_new_tasks(self) -> SomeTasks:
        get_telemetry = Task(TaskType.get_telemetry, TaskPriority.normal, [])
        return get_telemetry

    def terminate(self):
        super().set_terminate_flag()

        if settings.USE_CONTROLLER:
            self.xbox_controller.terminate()

        if settings.USE_CONTROLS_SOCKETS:
            self.controls_sockets_server.terminate()

        if settings.USE_TELEMETRY_SOCKETS:
            self.telemetry_sockets_client.terminate()

        if settings.USE_TOPSIDE_CLUI:
            self.ui.terminate()

        sleep(settings.THREAD_END_WAIT_S)

    def store_int_temp_data(self, int_temp: float):
        self.store_data(settings.TOPSIDE_INT_TEMP_NAME, int_temp)

    def store_controller_data(self, controller_data: dict):
        self.store_data(settings.CONTROLLER_NAME, controller_data)

    def serve_controller_data(self):
        controls = self.get_data(settings.CONTROLLER_NAME)
        if controls is None:
            return {}
        return controls

    def store_telemetry_data(self, telemetry_data: dict):
        self.store_data(settings.TELEMETRY_DATA_NAME, telemetry_data)

    def fetch_ui_data(self, key: str):
        return self.get_data(key)
