""" Sockets server for use in topside UI
"""

import json
import socket

import settings
from snr.async_endpoint import AsyncEndpoint
from snr.comms.sockets.config import SocketsConfig
from snr.utils import debug, sleep
from snr.node import Node


class SocketsServer(AsyncEndpoint):
    """Asynchronous sockets server which sends commands to robot
    """

    def __init__(self, parent: Node,
                 config: SocketsConfig, data_name: str):
        super().__init__(parent, "sockets_server", self.serve_data, 0)
        self.config = config
        self.datastore = self.parent.datastore

        self.data_name = data_name

        self.initialize_server()
        self.loop()

    def serve_data(self):
        # Create connection to a specific client
        # if not settings.USE_SOCKETS:
        #     self.set_terminate_flag()
        #     debug("sockets_server",
        #           "Exiting loop handler, sokcets not enabled in settings")
        #     return
        try:
            # Blocking call waiting for the client to connet
            self.accept_connection()
            # Send data to the client once it connects
            self.send_data()
        except (socket.timeout, OSError, Exception) as err:
            if err.__class__ is socket.timeout:
                debug("sockets_server",
                      "Restarting sockets server after idle timeout")
            else:
                debug("sockets_server",
                      "Connection failed: {}", [err.__repr__()])
                debug("sockets_server", "Restarting sockets server")
            self.close_socket()
            self.initialize_server()

    def initialize_server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(settings.SOCKETS_SERVER_TIMEOUT)
        # Use ethernet port
        # s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
        debug("sockets_status", "Socket created")
        try:
            host_tuple = self.config.tuple()
            debug("sockets_verbose", "Configuring with tuple: {}",
                  [host_tuple])
            self.s.bind(host_tuple)
            debug("sockets_event", "Socket bound to {}",
                  [self.config.tuple()])
        except socket.error as socket_error:
            debug("sockets_critical", "Bind failed: {}", [socket_error])
            self.s.close()
            sleep(settings.SOCKETS_RETRY_WAIT)
        try:
            self.s.listen(settings.SOCKETS_MAX_CONNECTIONS)
            debug("sockets_event", "Server now listening")
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
        # if not settings.USE_SOCKETS:
        #     return
        debug("sockets_event", "Blocking on accept_connection")
        # now keep talking with the client
        self.conn, self.addr = self.s.accept()

    def send_data(self):
        """Automatically send controls data as soon as the client connects.
        """
        controls = self.datastore.use(self.data_name)
        data = json.dumps(controls).encode()
        self.conn.sendall(data)
        debug("sockets_verbose", "Data sent")

    def close_socket(self):
        # if not settings.USE_SOCKETS:
        #     return
        try:
            self.s.close()
        except Exception as error:
            debug("sockets_error", "Error closing socket: {}",
                  [error.__repr__()])

    def terminate(self):
        self.close_socket()
        # settings.USE_SOCKETS = False
        debug("sockets_warn", "Socket closed")
