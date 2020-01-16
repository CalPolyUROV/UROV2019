import cv2
import socket
import pickle
import struct

#IP Address of the computer (Find using $ifconfig)
IP_ADDRESS = "10.155.115.129"
PORT = 8001

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP_ADDRESS, PORT))

# Create a VideoCapture object and read from input file
camera = cv2.VideoCapture(0)

# Check if camera opened successfully
if (camera.isOpened()== False): 
  print("Error opening video stream or file")

while True:
    try:
        grabbed, frame = camera.read()  # grab the current frame
        frame = cv2.resize(frame, (640, 480))  # resize the frame
        if grabbed == True:
            data = pickle.dumps(frame)
            message_size = struct.pack("=L", len(data))
            print(len(data))
            client_socket.sendall(message_size + data)
            
    except KeyboardInterrupt:
        camera.release()
        cv2.destroyAllWindows()
        print('exit')
        break
