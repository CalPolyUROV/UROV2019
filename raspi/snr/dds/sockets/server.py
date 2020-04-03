""" Sockets server for DDS
"""
import json
import socket
from typing import Union, Callable

from snr.async_endpoint import AsyncEndpoint
from snr.dds.sockets.config import SocketsConfig
from snr.utils.utils import sleep, no_op

import settings

context = "dds_sockets_server"


class SocketsServer(AsyncEndpoint):
    """Asynchronous sockets server which sends commands to robot
    """

    def __init__(self,
                 parent_node,
                 config: SocketsConfig,
                 callback: Callable):
        super().__init__(parent_node=parent_node, name=context,
                         setup_handler=no_op, loop_handler=self.receive_data,
                         tick_rate_hz=0)
        self.config = config
        self.callback = callback

        self.s = None
        self.ready = False
        self.connected = False
        # Async endpoint thread loop
        self.start_loop()

    def receive_data(self) -> Union[bytes, None]:
        self.diagnose()
        self.dbg("sockets_verbose",
                 "Waiting to receive data")
        try:
            data = self.s.recv(settings.MAX_SOCKET_SIZE)
            self.dbg("sockets_receive", "{} received data", [self.data_name])
            self.dbg("sockets_receive_verbose", "Received data: {}", [data])
            callback(data)
            # return data
        except (ConnectionResetError, Exception) as error:
            self.dbg("sockets_error", "Lost {} sockets connection: {}",
                     [self.name, error.__repr__()])
            return None

    def diagnose(self):
        if (not self.s) or (not self.ready):
            self.__init_socket()
        if not self.connected:
            self.__connect()

    def __init_socket(self):
        if self.s is not None:
            self.__close()

        # Create socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(settings.SOCKETS_SERVER_TIMEOUT)

        # Bind to the socket
        try:
            host_tuple = self.config.tuple()
            self.s.bind(host_tuple)
            self.dbg("sockets_event",
                     "Socket bound to {}",
                     [host_tuple])
        except socket.error as socket_error:
            self.dbg("sockets_critical",
                     "Bind failed: {}", [socket_error])
            self.s.close()
            sleep(settings.SOCKETS_RETRY_WAIT)
        # Listen for connections
        try:
            self.s.listen(settings.SOCKETS_MAX_CONNECTIONS)
            self.dbg("sockets_event", "Server now listening")
        except Exception as error:
            self.dbg("sockets_error", "Error listening: {}",
                     [error.__repr__()])
            self.s.close()
            return
        self.ready = True
        self.connected = False

    def __connect(self):
        # Create connection to the client
        try:
            # Blocking call waiting for the client to connect
            self.dbg("sockets_event",
                     "Blocking on accept_connection for {}",
                     [self.name])
            self.conn, self.addr = self.s.accept()
            self.connected = True
            return
        except (socket.timeout, OSError, Exception) as err:
            if isinstance(err, socket.timeout):
                self.dbg(context,
                         "Restarting sockets server after idle timeout")
            else:
                self.dbg(context,
                         "Connection failed: {}", [err.__repr__()])
            self.connected = False

    def __close(self):
        # if not settings.USE_SOCKETS:
        #     return
        try:
            self.s.close()
            self.s = None
            self.ready = False
            self.connected = False
        except Exception as error:
            self.dbg("sockets_error", "Error closing socket: {}",
                     [error.__repr__()])

    def terminate(self):
        self.__close()
        self.dbg("sockets_warn", "Socket closed")
