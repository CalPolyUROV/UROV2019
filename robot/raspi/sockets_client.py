"""Sockets client which communicates to topside raspi
"""

# System imports
import socket  # Sockets library
from sys import exit  # End the program when things fail
from time import sleep  # Wait before retrying sockets connection

from debug import debug  # Debug printing and logging
from debug import debug_f
import settings


class SocketsClient:
    """ Manages sockets network connection to topside raspi
    """

    def __init__(self, remote_ip='192.168.0.101', remote_port=5000):
        self.remote_ip = remote_ip  # Has defaut value
        self.remote_port = remote_port  # Has default value

        # Attempt to create a socket
        attempts: int = 0
        socket_open: bool = False
        while(not socket_open):
            try:
                # create an INET, STREAMing socket
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_open = True
            except socket.error:
                if (attempts > settings.SOCKETS_MAX_ATTEMPTS):
                    if(settings.REQUIRE_SOCKETS):
                        # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                        debug_f(
                            "sockets", "Could not create socket after {} attempts. Crashing now.", [attempts])
                        exit(1)
                    else:
                        debug_f("sockets", "Giving up on creating socket after {} attempts. Not required in settings.", [
                                attempts])
                        # TODO: Warn the rest of the system that sockets is not available
                        return
                attempts += 1
                debug("sockets", "Failed to create socket, trying again.")
                sleep(1)  # Wait a second before retrying
        debug("sockets", 'Socket Created')

    # Connect to remote server
    def connect_server(self):
        attempts: int = 0
        socket_open: bool = False
        while(not socket_open):
            try:
                self.s.connect((self.remote_ip, self.remote_port))
                socket_open = True
            except ConnectionRefusedError:
                if (attempts > settings.SOCKETS_MAX_ATTEMPTS):
                    if(settings.REQUIRE_SOCKETS):
                        # TODO: Handle aborting program in Schedule in order to correctly terminate connections, etc.
                        debug_f(
                            "socket_con", "Could not open socket after {} attempts. Crashing now.", [attempts])
                        exit(1)
                    else:
                        debug_f("socket_con", "Giving up on connecting to server after {} attempts.  Not required in settings.", [
                                attempts])
                        # TODO: Warn the rest of the system that sockets is not available
                        return
                attempts += 1
                debug("socket_con", "Failed to open socket, trying again.")
                sleep(1)  # Wait a second before retrying
        debug_f("socket_con", 'Socket Connected to {}:{}',
                [self.remote_ip, str(self.remote_port)])

    def send_data(self, message_str: str):

        message_enc = message_str.encode()

        while 1:
            # Send some data to remote server
            try:
                # Set the whole string
                self.s.sendall(message_enc)
            except socket.error:
                # Send failed
                debug("socket_con", 'Send failed')
                exit()

            debug("socket_con", 'Message send successfully')

            # Now receive data
            # BLocking call?
            reply = self.s.recv(4096)

            debug("socket_con", reply)
            return reply
            # sleep(1) # sleep for 1 second

    def close_socket(self):
        self.s.close()
        debug("socket_con", 'Socket closed')
