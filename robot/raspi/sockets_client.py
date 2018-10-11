# Socket client class for use on robot

# System imports
import socket # Sockets library
from sys import exit # End the program when things fail
from time import sleep # Wait before retrying sockets connection

# Maximum number of times to try openeing a socket
MAX_ATTEMPTS = 5 

class SocketsClient:

    def __init__(self, remote_ip='192.168.0.101', remote_port=5000):
        self.remote_ip = remote_ip # Has defaut value
        self.remote_port = remote_port # Has default value
        
        #create an INET, STREAMing socket
        # TODO: handle failure here verbosely
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            exit() # Bail out
            
        print('Socket Created')

    #Connect to remote server  
    def connect_server(self):
        attempts: int = 0
        socket_open: bool = False
        while(not socket_open):
            try:
                self.s.connect((self.remote_ip , self.remote_port))
                socket_open = True
            except ConnectionRefusedError:
                if (attempts > MAX_ATTEMPTS):
                    print("Could not open socket after {} attempts. Crashing now.".format(attempts))
                    exit(1)
                attempts += 1
                print("Failed to open socket, trying again.")
                sleep(1) # Wait a second before retrying
        print('Socket Connected to ' + self.remote_ip + ':' + str(self.remote_port))

    def send_data(self, message_str: str):
       
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
