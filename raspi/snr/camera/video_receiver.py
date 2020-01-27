""" Requires OpenCV2:
https://docs.opencv.org/master/d7/d9f/tutorial_linux_install.html
"""

import pickle
import socket
import struct
import numpy as np
import cv2

from snr.proc_endpoint import ProcEndpoint
from snr.node import Node

HOST = "localhost"

# Minimim area threshold that is boxed
AREA_THRESHHOLD = 1000

LINE_THICKNESS = 8

# Number of frames to skip to calculate the box
FRAME_SKIP_COUNT = 4

# Title of the window
WINDOW_TITLE = 'Video'

TICK_RATE_HZ = 0.0  # never sleep the server


class VideoReceiver(ProcEndpoint):
    """Video stream receiving endpoint.
    Shows video received over IP in window.
    """

    def __init__(self, parent: Node, name: str,
                 receiver_port: int):
        super().__init__(parent, name,
                         self.init_receiver, self.monitor_stream,
                         TICK_RATE_HZ)

        self.receiver_port = receiver_port
        self.start_loop()

    def init_receiver(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        self.s.bind((HOST, self.receiver_port))
        print('Socket bind complete')
        self.s.listen(10)
        print('Socket now listening')

        self.conn, self.addr = self.s.accept()

        self.data = b''  # CHANGED
        self.payload_size = struct.calcsize("=L")  # CHANGED

        # current frame counter
        self.count = 0

        # TODO: Split CV processing to alternate module
        self.rect_list = []

    def monitor_stream(self):
        try:
            # Retrieve message size
            while len(self.data) < self.payload_size:
                self.data += self.conn.recv(4096)

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("=L", packed_msg_size)[0]  # CHANGED

            # Retrieve all data based on message size
            while len(self.data) < msg_size:
                self.data += self.conn.recv(4096)

            frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]

            # Extract frame
            frame = pickle.loads(frame_data)

            self.count += 1

            if ((self.count % FRAME_SKIP_COUNT) == 0):
                self.rect_list = self.box_image(frame)

            for rects in self.rect_list:
                x, y, w, h = rects
                cv2.rectangle(frame, (x, y), (x+w, y+h),
                              (0, 255, 0), LINE_THICKNESS)

            # Display
            cv2.imshow('Raspberry Pi Stream', frame)
            cv2.waitKey(15)
        except KeyboardInterrupt:
            self.set_terminate_flag()

    def terminate(self):
        cv2.destroyAllWindows()

    # Function that takes in a image and draws boxes around suspected plants
    def box_image(self, img: np.array):
        """Sample CV method courtesy of the big J
        """
        # Converting image from BGR to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Generating the mask that outlines the plants
        # Method 1: Look for the color green
        mask1 = cv2.inRange(hsv, (30, 30, 30), (70, 255, 255))
        # Method 2

        # Take the mask and clean up the holes in the mask
        # Open removes area of the holes in the mask (removes noise) and
        # then adds area to the holes
        mask1 = cv2.morphologyEx(
            mask1, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        # Dilate areas in the mask (Add area to the holes in the mask)
        mask1 = cv2.morphologyEx(
            mask1, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))

        ret, thresh = cv2.threshold(mask1, 127, 255, 0)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
