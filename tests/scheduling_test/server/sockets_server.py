# Socket client server for use in topside UI

import socket
import sys
from time import sleep
 
class SocketsServer:

    def __init__(self, ip_address="192.168.10.10", port=5000):
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
                print("Bind failed. Error Code: {}".format(socket_error))
                self.s.close()
                sleep(1)
                continue
            self.bound = True  
        
        print('Socket bind to ' + str(self.ip_address) + ':' + str(self.port) + ' sucessful')
    
    def open_server(self):    
        self.s.listen(10)
    
        while 1:
            print('Socket now listening')

            #wait to accept a connection - blocking call
            conn, addr = self.s.accept()
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
            
            #now keep talking with the client
            while 1:
                data = conn.recv(1024)
                reply = 'OK...' + str(data)
                if not data: 
                    break
                print("Received: " + str(data))
                conn.sendall(reply.encode())
                print("Sent reply: \"" + reply + "\"")

            conn.close()
        self.close()
            
    def close(self):
        self.s.close()
        print('Socket closed')
