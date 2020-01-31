
from snr.async_endpoint import AsyncEndpoint
from snr.utils import debug
from snr.node import Node
from multiprocessing import Pool


class CameraManager(AsyncEndpoint):
    def __init__(self, parent: Node, name: str,
                 role: ManagerRole, camera_names: List[str]):
        super().__init__(parent, name,
                         self.setup_handler, self.loop_handler,
                         CAMERA_MANAGER_TICK_HZ)
        self.role = role
        self.camera_names = camera_names
        self.num_cameras = len(camera_names)
        self.port = INITIAL_PORT
        self.cameras = []
        # self.pool = Pool(num_cameras)

        # if role is ManagerRole.Receiver:

        #     return CameraManager(parent, name)
        # elif role is ManagerRole.Source:

        #     return CameraManager(parent, name)
        # else:
        #     debug("framework_error",
        #         "Unknown camera manager role {}",
        #         [role])

        self.start_loop()

    def setup_handler(self):
        if self.role is ManagerRole.Source:
            fac = VideoSourceFactory
        elif self.role is ManagerRole.Receiver:
            fac = VideoReceiverFactory

        # Create each camera process from pool
        for i, camera_name in enumerate(self.camera_names):
            config = CameraConfig(name,
                                  self.next_port(),
                                  self.next_cam_num())
            f = fac(config)
            self.cams[i] = f.get(self.parent)

    def loop_handler(self):
        pass

    def get(self) -> List:
        return [CameraPair(CameraConfig(name,
                                        self.next_port(),
                                        self.next_cam_num()))
                for name in self.camera_names]

    def next_port(self):
        val = self.port
        self.port += 2
        debug("camera_event",
              "Allocating port {} for camera {}",
              [val, self.cam_num])
        return val

    def next_cam_num(self):
        val = self.cam_num
        self.cam_num += 1
        return val
