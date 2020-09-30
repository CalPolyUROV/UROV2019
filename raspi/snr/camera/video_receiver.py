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
from snr.cv import find_plants
from snr.cv.boxes import apply_boxes

HOST = "localhost"

# Number of frames to skip to calculate the box
FRAME_SKIP_COUNT = 5

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
        self.window_name = f"Raspberry Pi Stream: {self.name}"
        self.count = 0  # Frame count
        self.boxes = []  # Cache of cv boxes
        self.start_loop()

    def init_receiver(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dbg("camera_event",
                     "{}: Socket created on {}",
                     [self.name, self.receiver_port])

            self.s.bind((HOST, self.receiver_port))
            self.s.listen(10)
            self.dbg("camera_event",
                     "{}: Socket now listening/blocking on {}",
                     [self.name, self.receiver_port])
            self.conn, self.addr = self.s.accept()
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise(e)
            else:
                self.set_terminate_flag(f"Exception: {e}")
                return

        self.data = b''
        self.payload_size = struct.calcsize("=L")

    def monitor_stream(self):
        try:
            # Retrieve message size
            while len(self.data) < self.payload_size:
                self.data += self.conn.recv(4096)

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("=L", packed_msg_size)[0]

            # Retrieve all data based on message size
            while len(self.data) < msg_size:
                self.data += self.conn.recv(4096)

            frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]

            # Extract frame
            frame = pickle.loads(frame_data)

            self.count += 1

            # Select frames for processing
            if ((self.count % FRAME_SKIP_COUNT) == 0):
                self.boxes = find_plants.box_image(frame)

            frame = apply_boxes(frame,
                                self.boxes,
                                find_plants.color,
                                find_plants.LINE_THICKNESS)

            # Display
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(15)
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise(e)
            self.dbg("camera_error",
                     "receiver monitor error: {}",
                     [e])
            self.set_terminate_flag(f"Exception: {e}")

    def terminate(self):
        cv2.destroyAllWindows()

        if self.s is not None:
            self.s.close()

        if self.count > 0:
            self.parent.datastore.store(f"{self.name}_recvd_frames",
                                        self.count)
            self.dbg(self.name,
                     "Dump recvd frames: {}",
                     [self.count])
