"""Thus begins the era of OpenCV dependancy.
https://docs.opencv.org/master/d7/d9f/tutorial_linux_install.html
"""

import socket
import pickle
import struct
import cv2
from cv2 import VideoCapture, destroyAllWindows

from snr.proc_endpoint import ProcEndpoint
from snr.node import Node
from snr.utils import debug

# IP Address of the computer (Find using $ifconfig)
# IP_ADDRESS = "10.155.115.129"
# PORT = 8001

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
TICK_RATE_HZ = 0.0


class VideoSource(ProcEndpoint):
    """USB camera video source for robot. Serves video over IP.
    """

    def __init__(self, parent: Node, name: str,
                 receiver_ip: str, receiver_port: int, camera_num: int):
        self.task_producers = []
        self.task_handlers = {}
        super().__init__(parent, name,
                         self.init_camera, self.send_frame, TICK_RATE_HZ)

        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.camera_num = camera_num

        self.start_loop()

    def init_camera(self):
        # Connect a client socket to my_server:8000 (change my_server to the
        # hostname of your server)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.receiver_ip, self.receiver_port))

        # Create a VideoCapture object and read from input file
        self.camera = VideoCapture(self.camera_num)

        # Check if camera opened successfully
        if (not self.camera.isOpened()):
            debug("camera_error",
                  "Error opening camera #{}",
                  [self.camera_num])

    def send_frame(self):
        try:
            grabbed, frame = self.camera.read()  # grab the current frame
            # resize the frame
            # frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            if grabbed:
                data = pickle.dumps(frame)
                size = len(data)
                message_size = struct.pack("=L", size)
                debug("camera_verbose",
                      "Sending frame data of size: {}",
                      [size])
                self.client_socket.sendall(message_size + data)

        except KeyboardInterrupt:
            self.set_terminate_flag()

    def terminate(self):
        self.camera.release()
        cv2.destroyAllWindows()
        debug("camera_event",
              "Closed video source (camera {})",
              [self.camera_num])
