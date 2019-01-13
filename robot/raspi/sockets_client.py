"""Sockets client which communicates to topside raspi
"""

# System imports
import socket  # Sockets library

# Our imports
import settings
from utils import sleep, exit, debug  # Debug printing and logging
from snr import ComsCon, Task, TaskType, TaskPriority, decode


class SocketsClient(ComsCon):
    """ Manages sockets network connection to topside raspi
    """

    def __init__(self, remote_ip=settings.TOPSIDE_IP_ADDRESS, remote_port=settings.TOPSIDE_PORT):
        self.remote_ip = remote_ip  # Has defaut value
        self.remote_port = remote_port  # Has default value

        self.socket_open = False
        self.socket_connected = False

        self.open_socket()

    def open_socket(self):
        if self.socket_open:
            # If socket is already open, KILLL it
            self.close()
        # Attempt to create a socket
        attempts = 1
        while(not self.create_socket()):
            if (attempts >= settings.SOCKETS_MAX_ATTEMPTS):
                if(settings.REQUIRE_SOCKETS):
                    # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                    debug(
                        "sockets_client", "Could not create socket after {} attempts.", [attempts])
                    exit("Could not create socket")
                else:
                    # Sockets connection not required by settings
                    debug("sockets_client", "Giving up on creating socket after {} attempts. Not required in settings.", [
                        attempts])
                    settings.USE_SOCKETS = False
                    return
            attempts += 1
            debug("sockets_client", "Trying again.")
            # Wait a second before retrying
            sleep(settings.SOCKETS_RETRY_WAIT)
        self.socket_open = True
        debug("sockets_client", 'Socket Created')

    def create_socket(self) -> bool:
        try:
            # create an INET, STREAMing socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return True
        except (Exception) as error:
            s = "Failed to create socket: {}"
            debug("sockets_client", s, [error.__repr__()])
            return False

    # Connect to remote server

    def connect(self):
        attempts = 1
        while(settings.USE_SOCKETS and not self.socket_connected and not self.connect_socket()):
            if (attempts >= settings.SOCKETS_CONNECT_ATTEMPTS):
                if(settings.REQUIRE_SOCKETS):
                    # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                    s = "Could not connect to server at {}:{} after {} attempts. Crashing now."
                    debug("socket_con", s, [
                          self.remote_ip, self.remote_port, attempts])
                    exit("Could not connect to server")
                else:
                    debug("socket_con", "Giving up on connecting to server after {} attempts.  Not required in settings.", [
                        attempts])
                    settings.USE_SOCKETS = False
                    return
            attempts += 1
            debug("socket_con", "Failed to connect to server at {}:{}, trying again.", [
                self.remote_ip, self.remote_port])
            # Wait a second before retrying
            sleep(settings.SOCKETS_RETRY_WAIT)
        self.socket_connected = True
        debug("socket_con", 'Socket Connected to {}:{}',
              [self.remote_ip, str(self.remote_port)])

    def connect_socket(self) -> bool:
        try:
            self.s.connect((self.remote_ip, self.remote_port))
            return True
        except (ConnectionRefusedError, Exception) as error:
            s = "Failed to connect to server: {}"
            debug("sockets_client", s, [error.__repr__()])
            return False

    def check_connection(self):
        if not self.socket_open:
            self.open_socket()
        if not self.socket_connected:
            self.connect()

    def repair_connection(self):
        self.close()
        self.open_socket()
        self.connect()

    def send_data(self, data: bytes) -> Task:
        """Main continual entry point for sending data over sockets

        This function must 
        """
        if not settings.USE_SOCKETS:
            debug("socket_con",
                  "Socket send ignored because settings.SOCKETS_USE = False")
            return
        self.check_connection()

        # Send data to remote server
        try:
            # Set the whole string
            self.s.sendall(data)
        except (OSError, Exception) as error:
            # Send failed
            debug("socket_con", 'Send failed: {}', [error.__repr__()])
            self.close_socket()
            return Task(TaskType.sockets_connect, TaskPriority.high, [])
            # exit("Sockets send failed")
        else:
            debug("socket_con", 'Message sent successfully')
            debug("socket_con_verbose", 'Message sent: {}', [data])

        # TODO: Handle loss of connection, attempt to recover

        # Now receive data
        reply = "Data not yet received"
        # BLocking call?
        try:
            reply = self.s.recv(settings.MAX_SOCKET_SIZE)
        except (ConnectionResetError, Exception) as error:
            self.socket_connected = False
            debug("sockets_client",
                  "Lost sockets connection: {}", error.__repr__())
            # TODO: Correctly terminate this function here
        else:
            debug("socket_con", "Received reply")
            debug("socket_con_verbose", "Received reply: {}", [reply])
            return reply

    def close_socket(self):
        try:
            self.s.close()
        except (Exception) as error:
            debug("sockets_client", "Error closing socket: {}",
                  [error.__repr__()])
        self.socket_open = False
        self.socket_connected = False
        debug("sockets_client", 'Socket closed')
