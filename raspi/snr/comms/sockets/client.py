"""Sockets client which communicates to a sockets server
"""

import json
import socket
from json import JSONDecodeError
from typing import Union

import settings
from snr.comms.sockets.config import SocketsConfig
from snr.endpoint import Endpoint
from snr.node import Node
from snr.task import SomeTasks, Task, TaskPriority
from snr.utils import attempt, debug, print_exit, sleep


class SocketsClient(Endpoint):
    """ Requests data from sockets server,
    located on the robot or topside unit
    """

    def __init__(self, parent: Node, name: str,
                 config: SocketsConfig, data_name: str):
        super().__init__(parent, name)

        self.config = config
        self.data_name = data_name
        self.s = None

        self.task_handlers = {
            f"get_{self.data_name}": self.task_handler
        }
        debug("sockets_status", "Sockets client created")

    def get_new_tasks(self) -> SomeTasks:
        return

    # Why a duplicate? is it an older version?
    # def task_handler(self, t: Task) -> SomeTasks:
    #     # Get controls input
    #     if t.task_type == "get_controls":
    #         controller_data = self.request_data()
    #         t = Task("process_controls",
    #                  TaskPriority.high, [controller_data])
    #         debug("robot_verbose",
    #               "Got task {} from controls sockets connection", [t])
    #         return t

    def task_handler(self, t: Task) -> SomeTasks:
        self.request_data()
        return Task("process_" + self.data_name, TaskPriority.high, [])

    def request_data(self):
        """Main continual entry point for sending data over sockets
        """
        self.create_connection()
        data_bytes = self.receive_data()
        self.close_socket()

        if data_bytes is None:
            # TODO: Throw an exception
            return

        data_str = data_bytes.decode()
        try:
            debug("decode_verbose",
                  "Decoded bytes as {}: {}",
                  [data_str.__class__, data_str])
            data_dict = json.loads(data_str)
            debug("decode_verbose", "Decoded control input: {}", [data_dict])
            self.parent.datastore.store(self.data_name, data_dict)

        except JSONDecodeError as error:
            debug("JSON_Error", "{}", [error])
            # TODO: Throw an exception
            return

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
                print_exit("Start required sockets connection")
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
