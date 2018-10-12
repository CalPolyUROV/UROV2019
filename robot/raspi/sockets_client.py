"""Sockets client which communicates to topside raspi
"""

# System imports
import socket  # Sockets library
from sys import exit  # End the program when things fail
from time import sleep  # Wait before retrying sockets connection

from debug import debug  # Debug printing and logging
from debug import debug_f

# Maximum number of times to try creating or openeing a socket
MAX_ATTEMPTS = 5


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
                if (attempts > MAX_ATTEMPTS):
                    debug_f(
                        "socket", "Could not create socket after {} attempts. Crashing now.", [attempts])
                    exit(1)
                attempts += 1
                debug("socket", "Failed to create socket, trying again.")
                sleep(1)  # Wait a second before retrying
        debug("socket", 'Socket Created')

    # Connect to remote server
    def connect_server(self):
        attempts: int = 0
        socket_open: bool = False
        while(not socket_open):
            try:
                self.s.connect((self.remote_ip, self.remote_port))
                socket_open = True
            except ConnectionRefusedError:
                if (attempts > MAX_ATTEMPTS):
                    debug_f(
                        "socket", "Could not open socket after {} attempts. Crashing now.", [attempts])
                    exit(1)
                attempts += 1
                debug("socket", "Failed to open socket, trying again.")
                sleep(1)  # Wait a second before retrying
        debug_f("socket", 'Socket Connected to {}:{}',
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
                debug("socket", 'Send failed')
                exit()

            debug("socket", 'Message send successfully')

            # Now receive data
            # BLocking call?
            reply = self.s.recv(4096)

            debug("socket", reply)
            return reply
            # sleep(1) # sleep for 1 second

    def close_socket(self):
        self.s.close()
        debug("socket", 'Socket closed')
