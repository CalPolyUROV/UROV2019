""" Sockets server for use in topside UI
"""
# System imports
import socket
import json

# Our imports
import settings
from snr import AsyncEndpoint
from task import *
from utils import debug, sleep

MAX_CONNECTIONS = 10


class SocketsServer(AsyncEndpoint):
    """Asynchronous sockets server which sends commands to robot
    """

    def __init__(self,  server_tuple: (str, int), get_data: Callable):
        if not settings.USE_SOCKETS:
            return
        super().__init__("sockets_server", self.loop_handler, 0)
        self.server_tuple = server_tuple
        self.get_data = get_data

        self.initialize_server()
        self.loop()


    def loop_handler(self):
        # Create connection to a specific client
        if not settings.USE_SOCKETS:
            self.set_terminate_flag()
            debug("sockets_server",
                  "Exiting loop handler, sokcets not enabled in settings")
            return
        try:
            # Blocking call waiting for the client to connet
            self.accept_connection()
            # Send data to the client once it connects
            self.send_data()
        except (socket.timeout, OSError, Exception) as err:
            if err.__class__ is socket.timeout:
                debug("sockets_server", "Restarting sockets server after idle timeout")
            else:
                debug("sockets_server",
                  "Connection failed: {}", [err.__repr__()])
                debug("sockets_server", "Restarting sockets server")
            self.close_socket()
            self.initialize_server()

    def initialize_server(self):
        if not settings.USE_SOCKETS:
            return

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(settings.SOCKETS_SERVER_TIMEOUT)
        # Use ethernet port
        # s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
        debug("sockets_status", "Socket created")
        try:
            self.s.bind(self.server_tuple)
            debug("sockets_event", "Socket bound to {}", [self.server_tuple])
        except socket.error as socket_error:
            debug("sockets_critical", "Bind failed: {}", [socket_error])
            self.s.close()
            sleep(settings.SOCKETS_RETRY_WAIT)
        try:
            self.s.listen(MAX_CONNECTIONS)
            debug("sockets_status", "Server now listening")
        except Exception as error:
            debug("sockets_error", "Error listening: {}", [error.__repr__()])
            self.s.close()

    def accept_connection(self):
        """Block until a client connects
        Once a clinet connects, the conn instance variable will be set so 
        send_data() can send data to it specifically. Note that only a single 
        instance variable conn can exist at once so the old connection is 
        overwritten on a new connection. The reason that this does not cause
        issues is that the client closes the old connection before connecting
        again.
        """
        if not settings.USE_SOCKETS:
            return
        debug("sockets_verbose", "Blocking on accept_connection")
        # now keep talking with the client
        self.conn, self.addr = self.s.accept()

    def send_data(self):
        """Automatically send controls data as soon as the client connects.
        """
        controls = self.get_data()
        data = json.dumps(controls).encode()
        self.conn.sendall(data)
        debug("sockets_verbose", "Data sent")

    def close_socket(self):
        if not settings.USE_SOCKETS:
            return
        try:
            self.s.close()
        except Exception as error:
            debug("sockets_error", "Error closing socket: {}",
                  [error.__repr__()])

    def terminate(self):
        self.close_socket()
        settings.USE_SOCKETS = False
        debug("sockets_warn", "Socket closed")
