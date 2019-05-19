"""This module keeps track of state for the motors on the robot

Takes in axis throttle information and manages state for the 6 thrusters on
the robot.

 6 ^ 2
 3 | 4
 5 | 1


   (Eyes Forward)
  /\     x      /\    
 /  \    A     /  \   
 \ 6 \   |    / 2 /    Z (Up)
  \  /   |    \  /    ^
   \/          \/    /    
   __           __  /
  /  \         /  \ 
 | 3  |   -->Y| 4  |
  \__/         \__/ 

  /\            /\  
 /  \          /  \ 
/ 5 /          \ 1 \
\  /            \  /
 \/              \/ 
Yaw is clockwise rotation of the XY Plane around the Z axis
Roll is rotation of the YZ Plane around the X axis
The thruster configuration does not enable Pitch control, which must be 
achieved by bouyancy
"""

from typing import Callable, List

from snr_task import Task, TaskType, TaskPriority, TaskScheduler, SomeTasks
import settings
from snr_utils import debug


class RobotMotors:
    def __init__(self, get_throttle_data: Callable):

        self.get_throttle_data = get_throttle_data

        self.motor_previous = generate_motor_array()
        self.motor_values = generate_motor_array()
        self.motor_targets = generate_motor_array()

    # def motor_control_tick(self):
    #     self.update_motor_targets(self.get_throttle_data())
    #     self.update_motor_values()
    #     self.generate_serial_tasks()
    #     # TODO: Send serial tasks to

    def update_motor_targets(self, axis):
        debug("motor_control", "Updating motor targets")
        # Motor 1: Forward, right
        self.motor_targets[0] = axis["x"] + axis["y"] - axis["yaw"]
        # Motor 2: Forward, left
        self.motor_targets[1] = 0 - axis["x"] + axis["y"] - axis["yaw"]
        # Motor 3, 4: Upwards
        self.motor_targets[2] = axis["z"] + axis["roll"]
        self.motor_targets[3] = axis["z"] - axis["roll"]
        # Motor 5: Forward, left
        self.motor_targets[4] = 0 - axis["x"] + axis["y"] + axis["yaw"]
        # Motor 6: Forward, right
        self.motor_targets[5] = axis["x"] + axis["y"] + axis["yaw"]

    def update_motor_values(self):
        for motor_index in range(settings.NUM_MOTORS):
            self.motor_previous[motor_index] = self.motor_values[motor_index]
            # New value is within max delta, set new value
            if (abs(self.motor_targets[motor_index] -
                    self.motor_values[motor_index])
                    <= settings.MOTOR_MAX_DELTA):
                self.motor_values[motor_index] = self.motor_targets[motor_index]

            # Target is above current
            elif self.motor_targets[motor_index] > self.motor_values[motor_index]:
                self.motor_values[motor_index] += settings.MOTOR_MAX_DELTA

            # Target is below current
            else:
                self.motor_values[motor_index] -= settings.MOTOR_MAX_DELTA

    def generate_serial_tasks(self) -> List[Task]:
        l = []
        for motor_index in range(settings.NUM_MOTORS):
            if not self.motor_values[motor_index] == self.motor_previous[motor_index]:
                t = Task(TaskType.serial_com, TaskPriority.high,
                         ["set_motor", motor_index, self.motor_values[motor_index]])
                l.append(t)

        debug("motor_control", "Generated {} serial task(s)", [len(l)])
        return l

    def terminate(self):
        pass


def generate_motor_array() -> List[int]:
    return [settings.DEFAULT_MOTOR_VALUE for i in range(settings.NUM_MOTORS)]
