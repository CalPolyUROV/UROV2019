#!/usr/bin/python3.5
"""Code for surface unit

Implements an SNR Node to use Sockets and a PyGame joystick to sent control data to robot
"""

# System imports
import socket

# Our imports
import settings
from controller import Controller
from snr import Node, Task, TaskPriority, TaskType, SomeTasks
from sockets_server import SocketsServer
from utils import debug, exit


class Topside(Node):

    def __init__(self):
        # TODO: implement SNR schedule/Node in topside
        # Create sockets server object
        self.start_sockets_server()
        # TODO: pass sockets server into Node/Schedule

        # TODO: Remotely run client on robot

        # Create controller object
        self.xbox_controller = Controller()
        self.task_queue = []

    def loop(self):
        while 1:
            # Create connection to a specific client
            try:
                self.sockets_server.accept_connection()
                while 1:
                    # Wait until cleint sends data, this is a blcoking call
                    self.sockets_server.recieve_data(
                        self.task_queue, self.handle_response)
            except (OSError, Exception) as err:
                debug("socket_con", "Socket connection failed: {}", [err])
                self.sockets_server.conn.close()
                self.sockets_server.close()

                debug("sockets_server", "Restarting sockets server")
                self.start_sockets_server()

    def execute_task(self, t: Task) -> SomeTasks:
        debug("execute_task", "Executing task: {} which is {}",
              [t, t.__class__.__name__])
        reply = None

        if (t.task_type == TaskType.debug_str):
            debug("execute_task", "Debug_str task: {}", [t.val_list])
            reply = Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"])

        elif (t.task_type == TaskType.get_cntl):
            # Handle accumulated commands

            reply = Task(TaskType.cntl_input, TaskPriority.high,
                         self.xbox_controller.get_input())
            # Previous test code:
            # if(len(task_queue) > 0):
            #     reply = task_queue.pop(0)
            # else:
            #     reply = Task(TaskType.blink_test, TaskPriority.normal, [200, 0])

        elif (t.task_type == TaskType.get_telemetry):
            debug("execute_task", "Executing task: {}", t.val_list)
            # TODO: Record and display telemetry data
            reply = Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"]) 

        else:
            debug("execute_task", "Unable to handle TaskType: {}, values: {}", [
                t.task_type, t.val_list])
            reply = Task(TaskType.cntl_input, TaskPriority.high,
                         ["This is a command"])

        return reply

    def start_sockets_server(self):
        self.sockets_server = None
        self.sockets_server = SocketsServer(
            settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)
        # TODO: Take IP address and port as command line arg
        # Open server port
        self.sockets_server.open_server()

    def terminate(self):
        self.xbox_controller.close()
