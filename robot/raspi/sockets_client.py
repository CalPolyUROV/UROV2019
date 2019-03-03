"""Sockets client which communicates to topside raspi
"""

# System imports
import socket  # Sockets library
from typing import Callable, Tuple

# Our imports
import settings
from snr import Relay, Handler
from task import *
from utils import debug, exit, sleep, attempt


class SocketsClient(Relay):
    """ Manages sockets network connection to topside raspi
    """

    def __init__(self, task_scheduler: Handler, server_tuple: Tuple[str, int]):
        super().__init__(self.request_data)
        self.server_tuple = server_tuple
        self.task_scheduler = task_scheduler
        self.s = None
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
        # debug("decode_verbose", "Decoded bytes as {}: {}", [data_str.__class__, data_str])
        data_dict = json.loads(data_str)
        debug("decode_verbose", "Decoded control input: {}", [data_dict])
        data_task = self.data_as_task(data_dict)
        debug("sockets_receive_verbose", "Got new task: {}", [data_task])
        return data_task

    def receive_data(self) -> Task:
        debug("sockets_verbose", "Waiting to receive data immediately upon connection")
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

    def data_as_task(self, controller_data: dict) -> Task:
        return Task(TaskType.cntl_input, TaskPriority.high, controller_data)

    def create_connection(self) -> None:
        """Create socket and connect to server in one function
        """
        if not settings.USE_SOCKETS:
            debug("sockets")
            return

        def try_create_connection() -> bool:
            try:
                self.s = socket.create_connection(
                    self.server_tuple, settings.SOCKETS_CLIENT_TIMEOUT)
                # Reuse port prior to slow kernel release
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return True
            except (ConnectionRefusedError, Exception) as error:
                s = "Failed to connect to server: {}"
                debug("sockets_client", s, [error.__repr__()])
                return False

        def fail_once() -> None:
            debug("sockets_warning", "Failed to connect to server at {}:{}, trying again.",
                  [self.server_tuple[0], str(self.server_tuple[1])])
            # Wait a second before retrying
            sleep(settings.SOCKETS_RETRY_WAIT)

        def failure(tries: int) -> None:
            if(settings.REQUIRE_SOCKETS):
                # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                s = "Could not connect to server at {}:{} after {} attempts. Exiting now."
                debug("sockets_critical", s, [
                    self.server_tuple[0], str(self.server_tuple[1]), tries])
                exit("Start required sockets connection")
            else:
                debug("ssockets_error", "Giving up on connecting to server after {} attempts.  Not required in settings.", [
                    tries])
                settings.USE_SOCKETS = False
                return

        attempt(try_create_connection,
                settings.SOCKETS_CONNECT_ATTEMPTS, fail_once, failure)
        self.socket_connected = True
        debug("sockets_event", 'Socket Connected to {}:{}',
              [self.server_tuple[0], str(self.server_tuple[1])])

    def close_socket(self):
        if self.s is None:
            debug("sockets_warning", "Tried to close socket but it was None")
            return
        try:
            # Close both (RD, WR) ends of the pipe, then close the socket
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
        except (Exception) as error:
            debug("sockets_error", "Error closing socket: {}",
                  [error.__repr__()])
        self.s = None
        debug("sockets_status", 'Socket closed')

    def terminate(self):
        self.close_socket()
        settings.USE_SOCKETS = False

    # def send_data(self, data: bytes) -> Task:
    #     if not settings.USE_SOCKETS:
    #         debug("sockets_warning",
    #               "Send ignored because sockets disabled in settings")
    #         return

    #     # Send data to remote server
    #     try:
    #         # Set the whole string
    #         self.s.sendall(data)
    #     except (OSError, Exception) as error:
    #         # Send failed
    #         debug("sockets_error", 'Send failed: {}', [error.__repr__()])
    #         # self.close_socket()
    #         # self.check_connection()
    #         # exit("Sockets send failed")
    #     else:
    #         debug("sockets_send", 'Message sent successfully')
    #         debug("sockets_send_verbose", 'Message sent: {}', [data])

    #     # TODO: Handle loss of connection, attempt to recover

    #     # Now receive data
    #     reply = "Data not yet received"
    #     # Blocking call?
    #     try:
    #         reply = self.s.recv(settings.MAX_SOCKET_SIZE)
    #         debug("sockets_receive", "Received reply")
    #         debug("sockets_receive_verbose", "Received reply: {}", [reply])
    #         task = decode(reply)
    #         return task
    #     except (ConnectionResetError, Exception) as error:
    #         self.socket_connected = False
    #         debug("sockets_error", "Lost sockets connection: {}",
    #               error.__repr__())
    #         # TODO: Correctly terminate this function here
