

# System imports
import socket

# Our imports
import settings
from controller import Controller
from snr import Node
from task import Task, TaskPriority, TaskType, SomeTasks
from sockets_server import SocketsServer
from utils import debug, exit, sleep
from internal_temp import IntTempMon
from topside_clui import TopsideClui


class Topside(Node):
    """Node for surface unit

    Implements an Node to use Sockets and a PyGame joystick to sent control 
    data to robot and show telemetry data from robot
    """
    def __init__(self, mode: str):
        super().__init__(self.execute_task, self.get_new_tasks)

        if mode.__eq__("debug"):
            settings.TOPSIDE_IP_ADDRESS = "localhost"

        # TODO: Remotely start robot program from topside

        # Start sockets server endpoint
        server_tuple = (settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)
        self.sockets_server = SocketsServer(
            server_tuple, self.get_data)
        # Start XBox controller endpoint
        self.xbox_controller = Controller(
            settings.CONTROLLER_NAME, super().store_data)
        # Start CLUI endpoint
        self.clui = TopsideClui(settings.TOPSIDE_CLUI_NAME, super().get_data)
        # Start local temperature monitor endpoint
        if settings.USE_TOPSIDE_PI_TEMP_MON:
            self.int_temp_mon = IntTempMon(
                "topside_pi_temperature", super().store_data)

        debug("framework", "Topside Node created")

    def execute_task(self, t: Task) -> SomeTasks:
        debug("execute_task", "Executing task: {} ", [t])
        sched_list = []

        if (t.task_type == TaskType.debug_str):
            debug("execute_task", "Debug_str task: {}", [t.val_list])
            
        elif (t.task_type == TaskType.get_telemetry):
            # TODO: Implement sockets client on topside to query server on robot for data
            pass

        else:
            debug("execute_task", "Unable to handle TaskType: {}, values: {}", [
                t.task_type, t.val_list])
           
        return sched_list

    def get_new_tasks(self) -> SomeTasks:
        get_telemetry = Task(TaskType.get_telemetry, TaskPriority.normal, [])
        return get_telemetry

    def terminate(self):
        super().set_terminate_flag()

        if settings.USE_CONTROLLER:
            self.xbox_controller.terminate()

        if settings.USE_SOCKETS:
            self.sockets_server.terminate()

        if settings.USE_TOPSIDE_PI_TEMP_MON:
            self.int_temp_mon.terminate()

        sleep(settings.THREAD_END_WAIT_S)
