"""Manage state for analog camera switching
"""

from snr_task import SomeTasks, Task, TaskPriority, TaskType
from snr_utils import debug


class RobotCameras:
    def __init__(self, num_cameras: int):
        self.num_cameras = num_cameras
        self.current_camera = 0
        self.serial_needs_update = True

    def next_state(self):
        if self.serial_needs_update:
            debug("cameras",
                  "Not switching, waiting for serial command to be sent")
            return
        self.current_camera += 1
        if self.current_camera >= self.num_cameras:
            self.current_camera = 0
        self.serial_needs_update = True
        debug("cameras", "Set to camera #{}", [self.current_camera])

    def set_camera(self, camera: int):
        if camera < self.num_cameras:
            self.current_camera = camera
            self.serial_needs_update = True
            debug("cameras", "Set to camera #{}", [self.current_camera])
        debug("cameras", "Cannot set to camera #{}, only have {} cameras",
              [self.current_camera, self.num_cameras])

    def get_task(self) -> SomeTasks:
        if self.serial_needs_update:
            self.serial_needs_update = False
            debug("cameras", "Produced task for serial cmd for camera #{}",
                  [self.current_camera])
            return Task(TaskType.serial_com,
                        TaskPriority.high,
                        ["set_cam", self.current_camera])
        return None
