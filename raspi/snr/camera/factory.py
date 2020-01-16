from typing import List

from snr.factory import Factory
from snr.async_endpoint import AsyncEndpoint
from snr.node import Node


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


class CameraManager:

    def __init__(self, camera_names: List[str]):
        self.names = camera_names
        self.cam_num = 0
        self.port = INITIAL_PORT

    def get(self) -> List:
        return [CameraPair(CameraConfig(name,
                                        self.next_port(),
                                        self.next_cam_num()))
                for name in self.names]

    def next_port(self):
        val = self.port
        self.port += 1
        return val

    def next_cam_num(self):
        val = self.cam_num
        self.cam_num += 1
        return val
