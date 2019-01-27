""" Sockets server for use in topside UI
"""
# System imports
import socket
import sys

# Our imports
import settings
from snr import Task, TaskPriority, TaskType, decode, Handler
from utils import debug, sleep


class SocketsServer:
    """ Manages sockets server which sends commands to robot

    This module is run by the topside unit under a separate thread
    TODO: verify this threading behavior
    """

    def __init__(self, handler: Handler, ip_address=settings.TOPSIDE_IP_ADDRESS, port=settings.TOPSIDE_PORT):
        self.server_tuple = ('', port)
        self.handler = handler
        self.bound = False

        while not self.bound:
            self.bind_to_port()

    def bind_to_port(self):
        # create socket, use ipv4
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Reuse port prior to slow kernel release
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set the timeout on the socket
        self.s.settimeout(settings.SOCKETS_SERVER_TIMEOUT)
        # Use ethernet port
        # s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
        debug("sockets_status", "Socket created")
        try:
            self.s.bind(self.server_tuple)
            debug("sockets_event", "Socket bound to {}",[self.server_tuple])
            self.bound = True
        except socket.error as socket_error:
            self.bound = False
            debug("sockets_critical", "Bind failed: {}", [socket_error])
            self.s.close()
            sleep(settings.SOCKETS_RETRY_WAIT)

    def open_server(self):
        self.s.listen(10)
        # TODO: Investigate this magic int

    def accept_connection(self,):
        debug("sockets_status", "Socket now listening")

        # wait to accept a connection - blocking call
        self.conn, self.addr = self.s.accept()
        debug("sockets_event", "Connected with {}:{}",
              [self.addr[0], self.addr[1]])

        # now keep talking with the client
        # Blocking?

    def recieve_data(self) -> None:
        data = self.conn.recv(settings.MAX_SOCKET_SIZE)
        if not data:
            debug("sockets_snafu", "Received empty data. Socket closed?")
            return
        debug("sockets_status", "Received data")
        debug("sockets_verbose", "Received data: {}", [data])

        # Decode data into task
        t = decode(data)
        # Handle data and respond
        reply = self.handler(t)
        debug("sockets_verbose", "Handled reply: {}", [reply])
        data = reply.encode()
        debug("sockets_verbose", "Encoded data: ",[data])
        self.conn.sendall(data)
        debug("sockets_status", 'Sent reply')
        debug("sockets_verbose", 'Sent reply: "{}"', [reply])

    def terminate(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        debug("sockets_warn", "Socket closed")

