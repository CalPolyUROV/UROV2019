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

# IP Address of the computer (Find using $ifconfig)
# IP_ADDRESS = "10.155.115.129"
# PORT = 8001

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
TICK_RATE_HZ = 120

DISPLAY_LOCALLY = False
USE_SOCKETS = True


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

        self.window_name = f"Video Source: {name}"

        self.frame_count = 0

        self.start_loop()

    def init_camera(self):
        if USE_SOCKETS:
            try:
                self.client_socket = socket.socket(socket.AF_INET,
                                                   socket.SOCK_STREAM)
                self.client_socket.connect((self.receiver_ip,
                                            self.receiver_port))
            except Exception as e:
                self.dbg("camera_error",
                         "Failed to connect to receiver: {}",
                         [e])
        else:
            self.dbg("camera",
                     "Not setting up sockets")
        try:
            # Create a VideoCapture object and read from input file
            self.camera = VideoCapture(self.camera_num)
        except Exception as e:
            self.dbg("camera_error", "Failed to open camera: {}", [e])

        # Check if camera opened successfully
        if (not self.camera.isOpened()):
            self.dbg("camera_error",
                     "Error opening camera #{}",
                     [self.camera_num])
        else:
            self.dbg("camera_open",
                     "Camera {}, {}: opened successfully",
                     [self.camera_num, self.name])

    def send_frame(self):
        try:
            grabbed, frame = self.camera.read()  # grab the current frame

            if DISPLAY_LOCALLY:
                # Display
                cv2.imshow(self.window_name, frame)
                cv2.waitKey(15)

            # resize the frame
            # frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            if grabbed and USE_SOCKETS:
                data = pickle.dumps(frame)
                size = len(data)
                message_size = struct.pack("=L", size)
                self.dbg("camera_verbose",
                         "{}: Sending frame data of size: {}",
                         [self.name, size])
                self.client_socket.sendall(message_size + data)
            self.frame_count += 1
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise e
            self.set_terminate_flag(f"Exception: {e}")

    def terminate(self):
        self.camera.release()

        if DISPLAY_LOCALLY:
            cv2.destroyAllWindows()

        self.dbg(f"{self.name}_source",
                 "Dump sent frames: {}",
                 [self.frame_count])
        self.parent.datastore.store(f"{self.name}_sent_frames",
                                    self.frame_count)

        self.dbg("camera_event",
                 "Closed video source (camera {})",
                 [self.camera_num])
