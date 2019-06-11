"""Sockets client which communicates to a sockets server
"""

import json
import socket
from json import JSONDecodeError
from typing import Union

import settings
from snr_sockets import SocketsConfig
from snr_task import SomeTasks, TaskScheduler
from snr_utils import attempt, debug, sleep, u_exit


class SocketsClient():
    """ Requests data from sockets server,
    located on the robot or topside unit
    """

    def __init__(self,
                 config: SocketsConfig,
                 task_scheduler: TaskScheduler):
        self.config = config
        self.task_scheduler = task_scheduler
        debug("sockets_status", "Sockets client created")

    def request_data(self) -> SomeTasks:
        """Main continual entry point for sending data over sockets
        """
        self.create_connection()
        # reply = self.send_data(data)
        data_bytes = self.receive_data()
        self.close_socket()

        if data_bytes is None:
            return None

        data_str = data_bytes.decode()
        try:
            debug("decode_verbose",
                  "Decoded bytes as {}: {}",
                  [data_str.__class__, data_str])
            data_dict = json.loads(data_str)
            debug("decode_verbose", "Decoded control input: {}", [data_dict])
            return data_dict
        except JSONDecodeError as error:
            debug("JSON_Error", "{}", [error])
            return None

    def receive_data(self) -> Union[bytes, None]:
        debug("sockets_verbose",
              "Waiting to receive data immediately upon connection")
        try:
            data = self.s.recv(settings.MAX_SOCKET_SIZE)
            debug("sockets_receive", "Received data")
            debug("sockets_receive_verbose", "Received data: {}", [data])
            return data
        except (ConnectionResetError, Exception) as error:
            self.socket_connected = False
            debug("sockets_error", "Lost sockets connection: {}",
                  error.__repr__())
            # TODO: Correctly terminate this function here
            return None

    def create_connection(self) -> None:
        """Create socket and connect to server in one function
        """
        # if not settings.USE_SOCKETS:
        #     debug("sockets")
        #     return

        def try_create_connection() -> bool:
            try:
                self.s = socket.create_connection(
                    self.config.tuple(),
                    settings.SOCKETS_CLIENT_TIMEOUT)
                # Reuse port prior to slow kernel release
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return True
            except (ConnectionRefusedError, Exception) as error:
                s = "Failed to connect to server: {}"
                debug("sockets_client", s, [error.__repr__()])
                return False

        def fail_once() -> None:
            debug("sockets_warning",
                  "Failed to connect to server at {}:{}, trying again.",
                  [self.config.ip,
                   str(self.config.port)])
            # Wait a second before retrying
            sleep(settings.SOCKETS_RETRY_WAIT)

        def failure(tries: int) -> None:
            if(self.config.required):
                debug("sockets_critical",
                      "Could not connect to server at {}:{} after {} tries.",
                      [self.config.ip, str(self.config.port), tries])
                u_exit("Start required sockets connection")
            else:
                debug("ssockets_error",
                      "Abort sockets connection after {} tries. Not required.",
                      [tries])
                # settings.USE_SOCKETS = False
                return

        attempt(try_create_connection,
                settings.SOCKETS_CONNECT_ATTEMPTS, fail_once, failure)
        self.socket_connected = True
        debug("sockets_event", 'Socket Connected to {}:{}',
              [self.config.ip, str(self.config.port)])

    def close_socket(self):
        if self.s is None:
            debug("sockets_warning", "Tried to close socket but it was None")
            return
        try:
            # Close both (RD, WR) ends of the pipe, then close the socket
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            debug("sockets_status", 'Socket closed')
        except (Exception) as error:
            debug("sockets_error", "Error closing socket: {}",
                  [error.__repr__()])
        self.s = None

    def terminate(self):
        # Not used since connection is short lived
        # self.close_socket()
        # settings.USE_SOCKETS = False
        pass
