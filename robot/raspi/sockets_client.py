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

        # Attempt to create a socket
        attempts = 1
        socket_open = False
        while(not socket_open):
            try:
                # create an INET, STREAMing socket
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_open = True
            except (Exception) as error:
                debug("sockets_client", "Create socket failed: {}", [error])
                if (attempts >= settings.SOCKETS_MAX_ATTEMPTS):
                    if(settings.REQUIRE_SOCKETS):
                        # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                        debug(
                            "sockets_client", "Could not create socket after {} attempts.", [attempts])
                        exit("Could not create socket")
                    else:
                        debug("sockets_client", "Giving up on creating socket after {} attempts. Not required in settings.", [
                            attempts])
                        settings.USE_SOCKETS = False
                        return
                attempts += 1
                debug("sockets_client", "Trying again.")
                # Wait a second before retrying
                sleep(settings.SOCKETS_RETRY_WAIT)
        debug("sockets_client", 'Socket Created')

    # Connect to remote server
    def connect_server(self):
        attempts = 1
        socket_open = False
        while(settings.USE_SOCKETS and not socket_open):
            try:
                self.s.connect((self.remote_ip, self.remote_port))
                socket_open = True
            except ConnectionRefusedError:
                if (attempts >= settings.SOCKETS_MAX_ATTEMPTS):
                    if(settings.REQUIRE_SOCKETS):
                        # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                        debug(
                            "socket_con", "Could not connect to server at {}:{} after {} attempts. Crashing now.", [self.remote_ip, self.remote_port, attempts])
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
        debug("socket_con", 'Socket Connected to {}:{}',
              [self.remote_ip, str(self.remote_port)])

    def send_data(self, data: bytes) -> Task:
        if (not settings.USE_SOCKETS):
            return
        while 1:
            # Send some data to remote server
            try:
                # Set the whole string
                self.s.sendall(data)
            except socket.error:
                # Send failed
                debug("socket_con", 'Send failed')
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
            except (ConnectionResetError) as error:
                debug("sockets_client",
                      "Lost sockets connection: {}", error.__repr__())
                # TODO: Handle conection reset here and reestablish connection

            debug("socket_con", "Received reply")
            debug("socket_con_verbose", "Received reply: {}", [reply])
            return reply
            # sleep(1) # sleep for 1 second

    def close_socket(self):
        self.s.close()
        debug("socket_con", 'Socket closed')
