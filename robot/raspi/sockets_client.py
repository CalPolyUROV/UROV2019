"""Sockets client which communicates to topside raspi
"""

# System imports
import socket  # Sockets library
from typing import Callable

# Our imports
import settings
from snr import Task, TaskPriority, TaskType, Transport, decode, Handler
from utils import debug, exit, sleep, attempt


class SocketsClient(Transport):
    """ Manages sockets network connection to topside raspi
    """

    def __init__(self, handler: Handler, remote_ip=settings.TOPSIDE_IP_ADDRESS, remote_port=settings.TOPSIDE_PORT):
        self.remote_ip = remote_ip  # Has defaut value
        self.remote_port = remote_port  # Has default value
        self.handler = handler
        self.s = None
        debug("sockets_status", "Sockets client created")

    def transport_data(self, data: bytes) -> None:
        """Main continual entry point for sending data over sockets
        """
        # self.create_socket()
        self.create_connection()
        reply = self.send_data(data)
        self.handler(reply)
        self.close_socket()

    def create_connection(self) -> None:
        """Create socket and connect to server in one function
        """
        server_tuple = (self.remote_ip, self.remote_port)

        def try_create_connection() -> bool:
            try:
                self.s = socket.create_connection(
                    server_tuple, settings.SOCKETS_CLIENT_TIMEOUT)
                # Reuse port prior to slow kernel release
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return True
            except (ConnectionRefusedError, Exception) as error:
                s = "Failed to connect to server: {}"
                debug("sockets_client", s, [error.__repr__()])
                return False

        def fail_once() -> None:
            debug("sockets_warning", "Failed to connect to server at {}:{}, trying again.",
                  [self.remote_ip, self.remote_port])
            # Wait a second before retrying
            sleep(settings.SOCKETS_RETRY_WAIT)

        def failure(tries: int) -> None:
            if(settings.REQUIRE_SOCKETS):
                # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                s = "Could not connect to server at {}:{} after {} attempts. Crashing now."
                debug("sockets_critical", s, [
                    self.remote_ip, self.remote_port, tries])
                exit("Could not connect to server")
            else:
                debug("ssockets_error", "Giving up on connecting to server after {} attempts.  Not required in settings.", [
                    tries])
                settings.USE_SOCKETS = False
                return

        attempt(try_create_connection,
                settings.SOCKETS_CONNECT_ATTEMPTS, fail_once, failure)
        self.socket_connected = True
        debug("sockets_event", 'Socket Connected to {}:{}',
              [self.remote_ip, str(self.remote_port)])

    def send_data(self, data: bytes) -> Task:
        if not settings.USE_SOCKETS:
            debug("sockets_warning",
                  "Send ignored because sockets disabled in settings")
            return

        # Send data to remote server
        try:
            # Set the whole string
            self.s.sendall(data)
        except (OSError, Exception) as error:
            # Send failed
            debug("sockets_error", 'Send failed: {}', [error.__repr__()])
            # self.close_socket()
            # self.check_connection()
            # exit("Sockets send failed")
        else:
            debug("sockets_send", 'Message sent successfully')
            debug("sockets_send_verbose", 'Message sent: {}', [data])

        # TODO: Handle loss of connection, attempt to recover

        # Now receive data
        reply = "Data not yet received"
        # Blocking call?
        try:
            reply = self.s.recv(settings.MAX_SOCKET_SIZE)
            debug("sockets_receive", "Received reply")
            debug("sockets_receive_verbose", "Received reply: {}", [reply])
            task = decode(reply)
            return task
        except (ConnectionResetError, Exception) as error:
            self.socket_connected = False
            debug("sockets_error", "Lost sockets connection: {}",
                  error.__repr__())
            # TODO: Correctly terminate this function here

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
        debug("sockets_client", 'Socket closed')
