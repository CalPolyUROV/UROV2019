import robot_data  # This is weird...

from task import *
from utils import debug, try_key


class Database:
    """Stores data for the robot
    Data includes sensor values and control inputs
    Implemented sensors:
        -None
    Senors TODO:
        -Acceleration and Orientation
        -Temperature (required by MATE comp)
        -pH (required by MATE comp)
        -Camera (if visible to python)

    Implemented inputs:
        - XBox Controller throttles
    Inputs TODO:
        -Mission tools
        -Camera switching
    """

    def __init__(self):
        """Create data structures to hold implented data
        """
        # Input data
        self.control_input = {}
        self.previous_cntl_input = {}

        # Internal data
        self.throttle = {'x': 0, 'y': 0, 'z': 0, "yaw": 0, "roll": 0}
        # Pitch is absent since motors are not arranged so

        # Output data
        self.acceleration = robot_data.GyroAccelData(0, 0, 0, 0, 0, 0)

    def telemetry_data(self) -> list:
        return [self.acceleration, self.orientation]

    def receive_controls(self, incoming_controls: dict) -> SomeTasks:
        self.previous_cntl_input = self.control_input
        self.control_input = incoming_controls
        if incoming_controls is None:
            return None
        return self.process_controls()

    def process_controls(self) -> SomeTasks:
        task_list = []
        # Collect only new control values
        for key in self.control_input.keys():
            old_data = try_key(self.previous_cntl_input, key)
            data = try_key(self.control_input, key)
            if data != old_data:
                # Decide what to do with a control input
                t = self.handle_control(key, data)
                if t is not None:
                    task_list.append(t)
            else:
                debug("robot_control_verbose", "Skipping unchanged value: {}", [data])

        # Batch thrust controls into a tasks afterwards
        task_list.append(self.handle_throttle())
        return task_list

    def handle_control(self, key: str, value) -> Task or []:
        """Deal with individual control buttons fromthe controller

        This method takes a key value pair from the control data dict and does
        the appropriate action for it. For joysticks and triggers, this is
        means settings a thrust value to be sent to the teensy. For these
        kinds of control values, process_throttle() is called. 
        """
        # TODO: Create task for different control inputs
        new_task = None
        if "stick" in key or "trigger" in key:
            self.process_throttle(key, value)
        return new_task

    def process_throttle(self, key: str, val):
        """Process the value of a single throttle control value

        This method is were the translation from a specific input on the
        XBox controller is translated to a direction in which to drive
        the ROV
        """

        # Left stick x axis to robot y axis
        if "stick_left_x" in key:
            self.throttle['y'] = val
            debug("thrust_vec_verbose", "Y set to {}", [self.throttle['y']])
        # Left stick y axis to robot x axis
        if "stick_left_y" in key:
            self.throttle['x'] = val
            # Invert stick Y axis
            debug("thrust_vec_verbose", "X set to {}", [self.throttle['x']])
        # Left trigger to robot descend (z axis)
        if "trigger_left" in key:
            self.throttle['z'] = 0 - val
            # Left trigger value is inverted to thrust downward
            debug("thrust_vec_verbose", "Z set to {}", [self.throttle['z']])
        # Left trigger to robot ascend (z axis)
        if "trigger_right" in key:
            self.throttle['z'] = val
            debug("thrust_vec_verbose", "Z set to {}", [self.throttle['z']])
        # Right stick x axis to robot yaw
        if "stick_right_x" in key:
            self.throttle["yaw"] = val
            debug("thrust_vec_verbose", "yaw set to {}", [self.throttle["yaw"]])
        # Right sick y axis to robot roll
        if "stick_right_y" in key:
            self.throttle["roll"] = val
            # Invert stick Y axis
            debug("thrust_vec_verbose", "roll set to {}", [self.throttle["roll"]])
        return

    def handle_throttle(self) -> Task or []:
        """Takes each throttle value and creates a task to send it to the teensy
        """
        # debug("thrust_vec", "Scheduling tasks for throttle values x:{}, y:{}, z:{}, yaw:{}, roll:{}", self.throttle)
        task_list = []

        task_list.append(Task(TaskType.serial_com, TaskPriority.high, [
                         "set_motor", 'x', self.throttle['x']]))
        task_list.append(Task(TaskType.serial_com, TaskPriority.high, [
                         "set_motor", 'y', self.throttle['y']]))
        task_list.append(Task(TaskType.serial_com, TaskPriority.high, [
                         "set_motor", 'z', self.throttle['z']]))
        task_list.append(Task(TaskType.serial_com, TaskPriority.high, [
                         "set_motor", 'yaw', self.throttle["yaw"]]))
        task_list.append(Task(TaskType.serial_com, TaskPriority.high, [
                         "set_motor", 'roll', self.throttle["roll"]]))

        return task_list


class GyroAccelData:
    def __init__(self, _x: int, _y: int, _z: int, _roll: int, _pitch: int, _yaw: int):
        self.x = _x
        self.y = _y
        self.z = _z
        self.roll = _roll
        self.pitch = _pitch
        self.yaw = _yaw

    def __repr__(self):
        return self.x.__repr__() + ", " + self.y.__repr__() + ", " + self.z.__repr__() + ", " + self.roll.__repr__() + ", " + self.pitch.__repr__() + ", " + self.yaw.__repr__()
