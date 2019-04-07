import robot_data  # This is weird...

from task import *
from utils import debug, try_key

# TODO: Split this class into robot_processing and return data storing to datastore.py


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
        if incoming_controls is None:
            debug("robot_control", "Received empty controls")
            return None
        self.previous_cntl_input = self.control_input
        self.control_input = incoming_controls
        task_list = self.process_controls()
        debug("robot_control", "Processed {} tasks from received controls", [len(task_list)])
        return task_list

    def process_controls(self) -> SomeTasks:
        task_list = []
        # Collect only new control values
        debug("robot_control_verbose", "Processing controls data: {}", [self.control_input])
        for key in self.control_input.keys():
            if self.previous_cntl_input is not None:
                old_data = try_key(self.previous_cntl_input, key)
            else:
                old_data = None
            data = try_key(self.control_input, key)
            if data != old_data:
                # Decide what to do with a control input
                t = self.handle_control(key, data)
                if t is not None:
                    task_list.append(t)
            else:
                debug("robot_control_verbose",
                      "Skipping unchanged value: {}", [data])

        # Batch thrust controls into a tasks afterwards
        throttle_tasks = self.get_throttle_tasks()
        # debug("thrust_vec", "Got {} throttle tasks", [len(throttle_tasks)])
        debug("thrust_vec_verbose", "Throttle tasks: {}", [throttle_tasks])
        for t in throttle_tasks:
            task_list.append(t)
        # debug("robot_control", "Processed {} tasks from controls", [len(task_list)])
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
            debug("throttle_verbose", "Y set to {}", [self.throttle['y']])
        # Left stick y axis to robot x axis
        if "stick_left_y" in key:
            self.throttle['x'] = val
            # Invert stick Y axis
            debug("throttle_verbose", "X set to {}", [self.throttle['x']])
        # Left trigger to robot descend (z axis)
        if "trigger_left" in key:
            # TODO: Disnetangle the two triggers for Z movement
            self.throttle['z'] = 0 - val
            # Left trigger value is inverted to thrust downward
            debug("throttle_verbose", "Z set to {}", [self.throttle['z']])
        # Left trigger to robot ascend (z axis)
        if "trigger_right" in key:
            self.throttle['z'] = val
            debug("throttle_verbose", "Z set to {}", [self.throttle['z']])
        # Right stick x axis to robot yaw
        if "stick_right_x" in key:
            self.throttle["yaw"] = val
            debug("throttle_verbose", "yaw set to {}",
                  [self.throttle["yaw"]])
        # Right sick y axis to robot roll
        if "stick_right_y" in key:
            self.throttle["roll"] = val
            # Invert stick Y axis
            debug("throttle_verbose", "roll set to {}",
                  [self.throttle["roll"]])
        return

    def get_throttle_tasks(self) -> Task or []:
        """Takes each throttle value and creates a task to send it to the teensy
        """
        debug("throttle", "Generating serial tasks for throttle values x:{}, y:{}, z:{}, yaw:{}, roll:{}",
              self.throttle_as_list())

        t_x = Task(TaskType.serial_com, TaskPriority.high,
                   ["set_motor", 'x', self.throttle['x']])
        t_y = Task(TaskType.serial_com, TaskPriority.high,
                   ["set_motor", 'y', self.throttle['y']])
        t_z = Task(TaskType.serial_com, TaskPriority.high,
                   ["set_motor", 'z', self.throttle['z']])
        t_yaw = Task(TaskType.serial_com, TaskPriority.high,
                     ["set_motor", 'yaw', self.throttle["yaw"]])
        t_roll = Task(TaskType.serial_com, TaskPriority.high,
                      ["set_motor", 'roll', self.throttle["roll"]])
        task_list = [t_x, t_y, t_z, t_yaw, t_roll]
        # debug("throttle", "Got {} tasks", [len(task_list)])
        # debug("throttle_verbose", "Tasks: {}", [task_list])
        return task_list

    def throttle_as_list(self) -> list:
        return [self.throttle['x'], self.throttle['y'], self.throttle['z'], self.throttle['yaw'], self.throttle['roll']]


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
