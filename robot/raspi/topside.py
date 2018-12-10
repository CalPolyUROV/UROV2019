#!/usr/bin/python3
"""Test code for surface unit focusing on sockets
"""

# Our imports
import settings
from utils import exit, debug, debug_f
from task import Task, TaskType, TaskPriority
from sockets_server import SocketsServer
from controller import Controller
from schedule import Node


class Topside(Node):

    def __init__(self):

        self.sockets_server = SocketsServer(
            settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)

        self.sockets_server.open_server()

        
        self.xbox_controller = Controller()
        self.task_queue = []

    def loop(self):
        while 1:
            self.sockets_server.accept_connection()
            while 1:
                self.sockets_server.recieve_data(self.task_queue, self.handle_response)

            self.sockets_server.conn.close()
            self.sockets_server.close()

    def handle_response(self, t: Task, task_queue: list) -> Task:
        debug_f("execute_task", "Executing task: {} which is {}",
                [t, t.__class__.__name__])
        reply = None

        if (t.task_type == TaskType.debug_str):
            debug_f("execute_task", "Debug_str task: {}", [t.val_list])
            t = Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"])
            reply = self(t, task_queue)

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
            debug_f("execute_task", "Executing task: {}", t.val_list)
            # TODO: Record and display telemetry data
            t = Task(TaskType.get_cntl, TaskPriority.high, [
                "Automatic control request in response of telemetry data"])
            reply = self(t, task_queue)

        else:
            debug_f("execute_task", "Unable to handle TaskType: {}, values: {}", [
                    t.task_type, t.val_list])
            reply = Task(TaskType.cntl_input, TaskPriority.high,
                         ["This is a command"])

        return reply

    def terminate(self):
        self.xbox_controller.close()
