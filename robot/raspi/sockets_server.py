""" Sockets server for use in topside UI
"""
# System imports
import socket
import sys

# Our imports
import settings
from utils import sleep, debug
from snr import Task, TaskType, TaskPriority, decode


class SocketsServer:
    """ Manages sockets server which sends commands to robot

    This module is run by the topside unit under a separate thread
    TODO: verify this threading behavior
    """

    def __init__(self, ip_address=settings.TOPSIDE_IP_ADDRESS, port=settings.TOPSIDE_PORT):
        self.ip_address = ip_address
        self.port = port
        self.bound = False

        while not self.bound:
            self.bind_to_port()
        debug("sockets", "Socket bound to {}:{} sucessfully",
              [self.ip_address, self.port])

    def bind_to_port(self):
        # create socket, use ipv4
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
        debug("sockets", "Socket created")
        try:
            self.s.bind((self.ip_address, self.port))
            self.bound = True
        except socket.error as socket_error:
            self.bound = False
            debug("sockets", "Bind failed: {}", [socket_error])
            self.s.close()
            sleep(settings.SOCKETS_RETRY_WAIT)

    def open_server(self):
        self.s.listen(10)
        # TODO: Investigate this magic int

    def accept_connection(self,):
        debug("socket_con", "Socket now listening")

        # wait to accept a connection - blocking call
        self.conn, self.addr = self.s.accept()
        debug("socket_con", "Connected with {}:{}",
              [self.addr[0], self.addr[1]])

        # now keep talking with the client
        # Blocking?

    def recieve_data(self, task_queue: list, handler):
        data = self.conn.recv(settings.MAX_SOCKET_SIZE)
        if not data:
            return
        debug("socket_con", "Received data")
        debug("socket_con_verbose", "Received data: {}", [data])

        # Decode data into task
        t = decode(data)
        # debug("socket_con", "Decoded data to task: {}", [t])
        # Handle data and respond
        reply = handler(t, task_queue)
        self.conn.sendall(reply.encode())
        # debug("socket_con", 'Sent reply: "{}"', [reply])
        debug("socket_con", 'Sent reply')

    def close(self):
        self.s.close()
        debug("socket_con", "Socket closed")
