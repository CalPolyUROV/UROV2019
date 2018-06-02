#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
 
#create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()
     
print('Socket Created')
 
host = 'www.google.com';
port = 5000;
 
try:
    remote_ip = socket.gethostbyname( host )
 
except socket.gaierror:
    #could not resolve
    print('Hostname could not be resolved. Exiting')
    sys.exit()

remote_ip = '192.168.0.101'
 
#Connect to remote server
s.connect((remote_ip , port))
 
print('Socket Connected to ' + host + ' on ip ' + remote_ip)
 
#Send some data to remote server
message = "GET / HTTP/1.1\r\n\r\n".encode()
 
try :
    #Set the whole string
    s.sendall(message)
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
 
print('Message send successfully')
 
#Now receive data
reply = s.recv(4096)
 
print(reply)
