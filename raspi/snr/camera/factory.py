from typing import List

from snr.endpoint_factory import EndpointFactory
from snr.async_endpoint import AsyncEndpoint
from snr.node import Node
from snr.camera.manager import CameraManager, ManagerRole
from snr.camera.config import CameraConfig


class VideoSourceFactory(EndpointFactory):
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


class VideoReceiverFactory(EndpointFactory):
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


class CameraManagerFactory(EndpointFactory):
    def __init__(self, role, camera_names):
        super().__init__()
        self.role = role
        self.camera_names = camera_names

    def get(self, parent: Node):
        return CameraManager(parent, f"video_{self.role.as_str()}_manager",
                             self.role, self.camera_names)

    def __repr__(self):
        return f"Camera Manager({self.role}) Factory"


class CameraManagerPair():
    def __init__(self, camera_names: List[str]):
        self.names = camera_names
        self.receiver = CameraManagerFactory(ManagerRole.Receiver,
                                             camera_names)
        self.source = CameraManagerFactory(ManagerRole.Source,
                                           camera_names)
