"""Node for surface unit

Implements an Node to use Sockets and a PyGame joystick to sent control data 
to robot
"""

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


class Topside(Node):

    def __init__(self, mode: str):
        super().__init__(self.execute_task, self.get_new_tasks)

        if mode.__eq__("debug"):
            settings.TOPSIDE_IP_ADDRESS = "localhost"

        # TODO: Remotely start robot program from topside

        # Create sockets server object
        server_tuple = (settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)
        self.sockets_server = SocketsServer(
            server_tuple, self.execute_task, self.get_data)
        # Create controller object
        self.xbox_controller = Controller(
            settings.CONTROLLER_NAME, super().store_data)
        # Start local temperature monitor
        if settings.USE_TOPSIDE_PI_TEMP_MON:
            self.int_temp_mon = IntTempMon(
                "topside_pi_temperature", super().store_data)

        debug("framework", "Topside Node created")

    def execute_task(self, t: Task) -> SomeTasks:
        debug("execute_task", "Executing task: {} which is {}",
              [t, t.__class__.__name__])
        if t is None:
            return None

        sched_list = []

        if (t.task_type == TaskType.debug_str):
            debug("execute_task", "Debug_str task: {}", [t.val_list])
            reply = Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"])

        elif (t.task_type == TaskType.get_cntl):
            # Handle accumulated commands

            sched_list.append(Task(TaskType.cntl_input, TaskPriority.high,
                                   self.get_controller_data()))
            # Previous test code:
            # if(len(task_queue) > 0):
            #     reply = task_queue.pop(0)
            # else:
            #     reply = Task(TaskType.blink_test, TaskPriority.normal, [200, 0])

        elif (t.task_type == TaskType.get_telemetry):
            debug("execute_task", "Executing task: {}", t.val_list)
            # TODO: Record and display telemetry data
            sched_list.append(Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"]))

        else:
            debug("execute_task", "Unable to handle TaskType: {}, values: {}", [
                t.task_type, t.val_list])
            # reply = Task(TaskType.cntl_input, TaskPriority.high, ["This is a command"])

        return sched_list

    def get_new_tasks(self) -> SomeTasks:
        # update_ui = Task(TaskType.update_ui, TaskPriority.high, [])
        get_telemetry = Task(TaskType.get_telemetry, TaskPriority.normal, [])
        task_list = [get_telemetry]
        return task_list

    def terminate(self):
        super().set_terminate_flag()

        if settings.USE_CONTROLLER:
            self.xbox_controller.terminate()

        if settings.USE_SOCKETS:
            self.sockets_server.terminate()

        if settings.USE_TOPSIDE_PI_TEMP_MON:
            self.int_temp_mon.terminate()

        sleep(settings.THREAD_END_WAIT_S)
