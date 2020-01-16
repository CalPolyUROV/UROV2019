import pickle
import socket
import struct
import numpy as np
import cv2

#IP address that means any client can try to connect
HOST = '0.0.0.0'
PORT = 8001

# Minimim area threshold that is boxed
AREA_THRESHHOLD = 1000

# Number of frames to skip to calculate the box
FRAME_SKIP_COUNT = 2

# Title of the window
WINDOW_TITLE = 'Video'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, addr = s.accept()

data = b'' ### CHANGED
payload_size = struct.calcsize("=L") ### CHANGED

# Function that takes in a image and draws boxes around suspected plants
def box_image(img: np.array):
    # Converting image from BGR to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Generating the mask that outlines the plants
    # Method 1: Look for the color green
    mask1 = cv2.inRange(hsv, (30, 30, 30), (70, 255,255))
    # Method 2

    # Take the mask and clean up the holes in the mask
    # Open removes area of the holes in the mask (removes noise) and then adds area to the holes
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    # Dilate areas in the mask (Add area to the holes in the mask)
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_DILATE, np.ones((3,3), np.uint8))

    ret,thresh = cv2.threshold(mask1, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # List of Rectangle objects
    rect_list = []
    # Loop through each of the "Plant" areas
    for c in contours:
        # if the "Plant" is large enough draw a rectangle around it
        if cv2.contourArea(c) > AREA_THRESHHOLD:
            # get the bounding rect
            x, y, w, h = cv2.boundingRect(c)
            rect_list.append((x, y, w, h))
            # draw a green rectangle to visualize the bounding rect
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 15)
    return rect_list

# current frame counter
count = 0
rect_list = []

while True:

    # Retrieve message size
    while len(data) < payload_size:
        data += conn.recv(4096)
	
    print("1")
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("=L", packed_msg_size)[0] ### CHANGED

    # Retrieve all data based on message size
    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    # Extract frame
    frame = pickle.loads(frame_data)

    count = count + 1
    if ((count % FRAME_SKIP_COUNT) == 0):
        rect_list = box_image(frame)
    for rects in rect_list:
        x, y, w, h = rects
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 15)

    # Display
    cv2.imshow('Raspberry Pi Stream', frame)
    cv2.waitKey(1)

