from typing import List

from enum import Enum
from snr.factory import Factory
from snr.async_endpoint import AsyncEndpoint
from snr.node import Node
from snr.utils import debug


class CameraConfig:
    def __init__(self, name, server_port, camera_num):
        self.name = name
        self.server_port = server_port
        self.camera_num = camera_num


class VideoSourceFactory(Factory):
    def __init__(self, config: CameraConfig):
        super().__init__()
        self.config = config

    def get(self, parent: Node) -> AsyncEndpoint:
        from snr.camera.video_source import VideoSource

        return VideoSource(parent, f"{self.config.name} source",
                           parent.datastore.get("node_ip_address"),
                           self.config.server_port,
                           self.config.camera_num)

    def __repr__(self):
        return f"Video(Cam: {self.config.camera_num}) Source Factory:{self.config.server_port}"


class VideoReceiverFactory(Factory):
    def __init__(self, config: CameraConfig):
        super().__init__()
        self.config = config

    def get(self, parent: Node) -> AsyncEndpoint:
        from snr.camera.video_receiver import VideoReceiver

        return VideoReceiver(parent, f"{self.config.name} receiver",
                             self.config.server_port)

    def __repr__(self):
        return f"Video Receiver Factory: {self.config.name}"


class CameraPair:
    def __init__(self, config):
        self.config = config

        self.source = VideoSourceFactory(self.config)
        self.receiver = VideoReceiverFactory(self.config)


INITIAL_PORT = 8000
CAMERA_MANAGER_TICK_HZ = 1


class ManagerRole(Enum):
    Source = 0
    Receiver = 1

    def __repr__(self):
        if (self is Source):
            return "Source"
        else:
            return "Receiver"



class CameraManagerFactory(Factory):
    def __init__(self, role, camera_names):
        super().__init__()
        self.role = role
        self.camera_names = camera_names

    def get(self, parent: Node):
        return CameraManager(parent, f"{self.role}",
                             self.role, self.camera_names)

    def __repr__(self):
        return f"Camera Manager factory for {self.role}"


class CameraManagerPair():
    def __init__(self, camera_names: List[str]):
        self.names = camera_names
        # self.cam_num = 0
        # self.port = INITIAL_PORT
        self.receiver = CameraManagerFactory(
            ManagerRole.Receiver, camera_names)
        self.source = CameraManagerFactory(ManagerRole.Source, camera_names)