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
The thruster configuration does not enable Pitch control, which must
be achieved by bouyancy
"""

from typing import Callable, List

import settings
from snr.async_endpoint import AsyncEndpoint
from snr.task import SomeTasks, Task, TaskPriority, TaskType
from snr.utils import Profiler, debug
from snr.factory import Factory
from snr.datastore import Datastore
from snr.endpoint import Endpoint


class RobotMotorsFactory(Factory):
    def __init__(self, input_data_name: str,
                 output_data_name: str):
        super().__init__()
        self.input_data_name = input_data_name
        self.output_data_name = output_data_name

    def get(self, mode: str,
            profiler: Profiler,
            datastore: Datastore) -> Endpoint:
        return RobotMotors(mode, profiler, datastore,
                           self.input_data_name, self.output_data_name)


class RobotMotors(AsyncEndpoint):
    def __init__(self, mode: str, profiler: Profiler, datastore: Datastore,
                 input_name: str, output_name: str):

        super().__init__("robot_motors", self.update_motor_values,
                         settings.MOTOR_CONTROL_TICK_RATE, profiler)
        self.input_data_name = input_name

        self.motor_previous = generate_motor_array()
        self.motor_values = generate_motor_array()
        self.motor_targets = generate_motor_array()

        self.loop()

    def get_throttle_data(self):
        return self.datastore.use(self.input_data_name)

    # def motor_control_tick(self):
    #     self.update_motor_targets(self.get_throttle_data())
    #     self.update_motor_values()
    #     self.generate_serial_tasks()
    #     # TODO: Send serial tasks to

    def update_motor_targets(self, axis):
        debug("motor_control_verbose", "Updating motor targets")
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
        for index in range(settings.NUM_MOTORS):
            self.motor_previous[index] = self.motor_values[index]
            # New value is within max delta, set new value
            if (abs(self.motor_targets[index] -
                    self.motor_values[index])
                    <= settings.MOTOR_MAX_DELTA):
                self.motor_values[index] = self.motor_targets[index]

            # Target is above current
            elif self.motor_targets[index] > self.motor_values[index]:
                self.motor_values[index] += settings.MOTOR_MAX_DELTA

            # Target is below current
            else:
                self.motor_values[index] -= settings.MOTOR_MAX_DELTA

    def generate_serial_tasks(self) -> SomeTasks:
        task_list = []
        for index in range(settings.NUM_MOTORS):
            if not self.motor_values[index] == self.motor_previous[index]:
                t = Task(TaskType.serial_com, TaskPriority.high,
                         ["set_motor", index, self.motor_values[index]])
                task_list.append(t)

        debug("motor_control", "Generated {} serial task(s)", [len(task_list)])
        debug("motor_control_verbose", "{}", [task_list])
        return task_list

    def terminate(self):
        pass


def generate_motor_array() -> List[int]:
    return [settings.DEFAULT_MOTOR_VALUE for i in range(settings.NUM_MOTORS)]
