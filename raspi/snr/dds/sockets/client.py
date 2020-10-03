"""Sockets client which communicates to a sockets server
"""

import json
from snr.context import Context
import socket

from snr.dds.sockets.config import SocketsConfig
from snr.utils.utils import attempt, print_exit


class SocketsClient(Context):
    def __init__(self,
                 parent_context: Context,
                 config: SocketsConfig):
        super().__init__("dds_sockets_client", parent_context)
        self.config = config

        self.create_connection()

    def send_data(self, data):
        if data is None:
            self.warn(
                "Data is none for {}",
                [self.data_name])
        encoded_data = json.dumps(data).encode()
        self.conn.sendall(encoded_data)
        self.info("Data sent")

    def create_connection(self) -> None:
        """Create socket and connect to server in one function
        """
        # if not settings.USE_SOCKETS:
        #     self.dbg("sockets")
        #     return

        def try_create_connection() -> bool:
            try:
                self.s = socket.create_connection(
                    self.config.tuple(),
                    self.settings.SOCKETS_CLIENT_TIMEOUT)
                # Reuse port prior to slow kernel release
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return True
            except (ConnectionRefusedError, Exception) as error:
                self.dbg("Failed to connect to server: {}",
                         [error.__repr__()])
                return False

        def fail_once() -> None:
            self.warn("Failed to connect to server at {}:{}, trying again.",
                      [self.config.ip, str(self.config.port)])
            # Wait a second before retrying
            self.sleep(self.settings.SOCKETS_RETRY_WAIT)

        def failure(tries: int) -> None:
            if(self.config.required):
                self.critical(
                    "Couldn't connect to server at {}:{} after {} tries.",
                    [self.config.ip, str(self.config.port), tries])
                print_exit("Start required sockets connection")
            else:
                self.err(
                    "Aborted connection after {} tries. Not required.",
                    [tries])
                # settings.USE_SOCKETS = False
                return

        attempt(try_create_connection,
                self.settings.SOCKETS_CONNECT_ATTEMPTS, fail_once, failure)
        self.socket_connected = True
        self.dbg('Socket Connected to {}:{}',
                 [self.config.ip, str(self.config.port)])

    def close_socket(self):
        if self.s is None:
            self.warn(
                "Tried to close socket but it was None")
            return
        try:
            # Close both (RD, WR) ends of the pipe, then close the socket
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.info('Socket {} closed', [self.name])
        except (Exception) as error:
            self.err("Error closing socket {}: {}",
                     [self.name, error.__repr__()])
        self.s = None

    def terminate(self):
        # Not used since connection is short lived
        # self.close_socket()
        # settings.USE_SOCKETS = False
        pass
