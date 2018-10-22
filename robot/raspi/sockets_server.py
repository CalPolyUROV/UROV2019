""" Sockets server for use in topside UI
"""
# System imports
import socket
import sys
from time import sleep

# Our imports
import settings
from task import *
from debug import debug
from debug import debug_f


class SocketsServer:
    """ Manages sockets server which sends commands to robot
    """

    def __init__(self, ip_address=settings.TOPSIDE_IP_ADDRESS, port=settings.TOPSIDE_PORT):
        self.ip_address = ip_address
        self.port = port
        self.bound = False

        while not self.bound:
            # create socket, use ipv4
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
            print('Socket created')
            try:
                self.s.bind((self.ip_address, self.port))
            except socket.error as socket_error:
                self.bound = False
                debug_f("sockets", "Bind failed. Error Code: {}",
                        [socket_error])
                self.s.close()
                sleep(1)
                continue
            self.bound = True  
        
        debug_f("sockets", 'Socket bound to {}:{} sucessfully', [self.ip_address, self.port])
    
    def open_server(self):    
        self.s.listen(10)

        while 1:
            debug("socket_con", 'Socket now listening')

            # wait to accept a connection - blocking call
            conn, addr = self.s.accept()
            debug_f("socket_con", 'Connected with {}:{}', [addr[0], addr[1]])

            # now keep talking with the client
            # Blocking?
            while 1:
                # Recieve data
                data: bytes = conn.recv(settings.MAX_SOCKET_SIZE)
                if (not data):
                    break
                debug_f("socket_con", "Received: {}", [data])
                reply = handle_response(decode(data))
                conn.sendall(reply.encode())
                debug_f("socket_con", "Sent reply: \"{}\"", [reply])

            conn.close()
        self.close()

    def close(self):
        self.s.close()
        debug("socket_con", 'Socket closed')
