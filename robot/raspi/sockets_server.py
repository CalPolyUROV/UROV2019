""" Sockets server for use in topside UI
"""
# System imports
import socket
import sys
from time import sleep

# Our imports
import settings
from task import Task
from task import TaskType
from task import TaskPriority
from task import decode
from debug import debug
from debug import debug_f


class SocketsServer:
    """ Manages sockets server which sends commands to robot
    """

    def __init__(self, ip_address=settings.TOPSIDE_IP_ADDRESS, port=settings.TOPSIDE_PORT):
        self.ip_address = ip_address
        self.port = port
        self.bound = False

        while not self.bound:
            # create socket, use ipv4
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
            debug("sockets", 'Socket created')
            try:
                self.s.bind((self.ip_address, self.port))
            except socket.error as socket_error:
                self.bound = False
                debug_f("sockets", "Bind failed. Error Code: {}",
                        [socket_error])
                self.s.close()
                sleep(1)
                continue
            self.bound = True

        debug_f("sockets", 'Socket bound to {}:{} sucessfully',
                [self.ip_address, self.port])

    def handle_response(self, t: Task) -> Task:
        debug_f("execute_task", "Executing task: {} which is {}", [t, t.__class__.__name__])
        reply = None
        if (t.task_type == TaskType.debug_str):
            debug_f("execute_task", "Debug_str task: {}", [t.val_list])
            t = Task(TaskType.get_cntl, TaskPriority.high, ["Automatic control request in response of telemetry data"])
            reply = self.handle_response(t)

        elif (t.task_type == TaskType.get_cntl):
            # Handle accumulated commands
            t = Task(TaskType.cntl_input, TaskPriority.normal, [
                           "do stuff", 1, 2, "3"])
            reply = t

        elif (t.task_type == TaskType.get_telemetry):
            debug_f("execute_task", "Executing task: {}", t.val_list)
            # TODO: handle telemetry data
            t = Task(TaskType.get_cntl, TaskPriority.high, [
                           "Automatic control request in response of telemetry data"])
            reply = self.handle_response(t)

        else:
            debug_f("execute_task", "Unable to handle TaskType: {}, values: {}", [
                    t.task_type, t.val_list])
            reply = Task(TaskType.cntl_input, TaskPriority.high,
                         ["This is a command"])
        return reply

    def open_server(self):
        self.s.listen(10)

        while 1:
            debug("socket_con", 'Socket now listening')

            # wait to accept a connection - blocking call
            conn, addr = self.s.accept()
            debug_f("socket_con", 'Connected with {}:{}', [addr[0], addr[1]])

            # now keep talking with the client
            # Blocking?
            while 1:
                # Recieve data
                data = conn.recv(settings.MAX_SOCKET_SIZE)
                if (not data):
                    break
                debug_f("socket_con", "Received data: {}", [data])
                # Decode data into task
                t = decode(data)
                debug_f("socket_con", "Decoded data to task: {}", [t])
                # Handle data and respond
                reply = self.handle_response(t)
                conn.sendall(reply.encode())
                debug_f("socket_con", "Sent reply: \"{}\"", [reply])

            conn.close()
        self.close()

    def close(self):
        self.s.close()
        debug("socket_con", 'Socket closed')
