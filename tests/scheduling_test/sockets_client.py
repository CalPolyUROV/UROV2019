#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
# from time import sleep

class SocketsClient:

    def __init__(self, remote_ip='192.168.0.101', remote_port=5000):
        self.remote_ip = remote_ip # Has defaut value
        self.remote_port = remote_port # Has default value
        self.s = self.initialize_socket() # Start the socket 

    def initialize_socket(self):
        #create an INET, STREAMing socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit() # Bail out
            
        print('Socket Created')
                    
        return s

    def send_data(self, message_str: str):
        #Connect to remote server
        self.s.connect((self.remote_ip , self.remote_port))
        
        print('Socket Connected to ' + self.remote_ip + ':' + str(self.remote_port))

        message_enc = message_str.encode()

        while 1:
            #Send some data to remote server     
            try :
                #Set the whole string
                self.s.sendall(message_enc)
            except socket.error:
                #Send failed
                print('Send failed')
                sys.exit()
            
            print('Message send successfully')
            
            # Now receive data
            # BLocking call?
            reply = self.s.recv(4096)
            
            print(reply)
            return reply
            # sleep(1) # sleep for 1 second

            
    def close_socket(self):
        self.s.close()
        print('Socket closed')
