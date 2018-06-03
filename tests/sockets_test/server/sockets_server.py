import socket
import sys
from time import sleep
 
HOST = '192.168.10.10'   # Symbolic name meaning all available interfaces
PORT = 5000 # Arbitrary non-privileged port


bound = False
while not bound:
    # create socket, use ipv4 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')
    print('Socket created')
    try:
        s.bind((HOST, PORT))
    except socket.error as socket_error:
        bound = False
        print('Bind failed. Error Code: '.format(socket_error))
        s.close()
        sleep(1)
        continue
        #sys.exit()
    bound = True  
     
print('Socket bind to ' + str(HOST) + ':' + str(PORT) + ' sucessful')
 
s.listen(10)
while 1:
    print('Socket now listening')

    #wait to accept a connection - blocking call
    conn, addr = s.accept()
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
    
s.close()
print('Socket closed')
