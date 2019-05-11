from typing import Any, List

import settings
from robot_cameras import RobotCameras
from snr_datastore import DatastoreSetter
from snr_task import SomeTasks, Task, TaskPriority, TaskType
from snr_utils import debug, try_key

# TODO: Split this class into robot_processing and datastore.py


class ControlsProcessor:
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

    def __init__(self, db_store_throttle: callable):
        """Create data structures to hold implented data
        """
        self.db_store_throttle = db_store_throttle
        self.cameras = RobotCameras(settings.NUM_ANALOG_CAMERAS)
        # Input data
        self.control_input = {}
        self.previous_cntl_input = {}

        # Internal data
        self.axis_list = ['x', 'y', 'z', "yaw", "roll"]
        self.previous_throttle = self.init_dict(self.axis_list, 0)
        self.throttle = self.init_dict(self.axis_list, 0)

        self.buttons_list = ['a']
        self.buttons = self.init_dict(self.buttons_list, False)
        self.previous_buttons = self.init_dict(self.buttons_list, False)
        # Pitch cannot be acheive with current motor configuration

    def init_dict(self, keys: List[str], val: Any) -> dict:
        d = {}
        for k in keys:
            d[k] = val
        return d

    def receive_controls(self, incoming_controls: dict) -> SomeTasks:
        if incoming_controls is None:
            debug("robot_control_warning", "Received empty controls")
            return None
        self.previous_cntl_input = self.control_input
        self.control_input = incoming_controls
        task_list = self.process_controls()
        debug("robot_control_event",
              "Processed {} tasks from received controls", [len(task_list)])
        return task_list

    def process_controls(self) -> List[Task]:
        task_list = []
        # Collect only new control values
        debug("robot_control_verbose",
              "Processing controls data: {}", [self.control_input])
        for key in self.control_input.keys():
            # For each key that is incoming
            # if self.previous_cntl_input is not None:
            old_data = try_key(self.previous_cntl_input, key)
            # else:
            #     old_data = None
            data = self.control_input[key]

            if not data == old_data:
                # Decide what to do with a control input
                t = self.handle_control(key, data)
                if t is not None:
                    task_list.append(t)
            else:
                debug("robot_control_verbose",
                      "Skipping unchanged value: {}", [data])

        # Batch thrust controls into a tasks afterwards
        throttle_tasks = self.get_throttle_tasks()
        camera_tasks = self.cameras.get_task()
        # debug("thrust_vec", "Got {} throttle tasks", [len(throttle_tasks)])
        debug("thrust_vec_verbose", "Throttle tasks: {}",
              [throttle_tasks, camera_tasks])
        task_list.append(throttle_tasks)
        task_list.append(camera_tasks)
        debug("robot_control_event", "Created {} tasks from controls",
              [len(task_list)])
        return task_list

    def handle_control(self, key: str, value) -> SomeTasks:
        """Deal with individual control buttons from the controller
        This method takes a key value pair from the control data dict and does
        the appropriate action for it. For joysticks and triggers, this is
        means settings a thrust value to be sent to the teensy. For these
        kinds of control values, process_throttle() is called.
        """
        # TODO: Create task for different control inputs
        new_task = None
        if "stick" in key or "trigger" in key:
            self.process_throttle(key, value)
        elif "button" in key:
            self.process_button(key, value)
        return new_task

    def process_throttle(self, key: str, val):
        """Process the value of a single throttle control value
        This method is were the translation from a specific input on the
        XBox controller is translated to a direction in which to drive
        the ROV
        """

        # Left stick x axis to robot y axis
        if "stick_left_x" in key:
            self.previous_throttle['y'] = self.throttle['y']
            self.throttle['y'] = val
            debug("throttle_verbose", "Y set to {}", [self.throttle['y']])
        elif "stick_left_y" in key:
            # Left stick y axis to robot x axis
            self.previous_throttle['x'] = self.throttle['x']
            self.throttle['x'] = val
            # Invert stick Y axis
            debug("throttle_verbose", "X set to {}", [self.throttle['x']])
        elif "trigger_left" in key:
            # Left trigger to robot descend (z axis)
            # TODO: Disnetangle the two triggers for Z movement
            self.previous_throttle['z'] = self.throttle['z']
            self.throttle['z'] = 0 - val
            # Left trigger value is inverted to thrust downward
            debug("throttle_verbose", "Z set to {}", [self.throttle['z']])
        elif "trigger_right" in key:
            # Left trigger to robot ascend (z axis)
            self.previous_throttle['z'] = self.throttle['z']
            self.throttle['z'] = val
            debug("throttle_verbose", "Z set to {}", [self.throttle['z']])
        elif "stick_right_x" in key:
            # Right stick x axis to robot yaw
            self.previous_throttle['yaw'] = self.throttle['yaw']
            self.throttle["yaw"] = val
            debug("throttle_verbose", "yaw set to {}",
                  [self.throttle["yaw"]])
        elif "stick_right_y" in key:
            # Right sick y axis to robot roll
            self.previous_throttle['roll'] = self.throttle['roll']
            self.throttle["roll"] = val
            # Invert stick Y axis
            debug("throttle_verbose", "roll set to {}",
                  [self.throttle["roll"]])
        return

    def get_throttle_tasks(self) -> Task or []:
        """Takes each throttle value and creates a task to send it to the teensy
        """
        debug("throttle_verbose", "Generating tasks for throttle values")
        s = "x:{}, y:{}, z:{}, yaw:{}, roll:{}"
        debug("throttle_values", s, self.throttle_value_list())

        task_list = []
        for axis in self.axis_list:
            if self.axis_changed(axis):
                t = Task(TaskType.serial_com, TaskPriority.high,
                         ["set_motor", axis, self.throttle[axis]])
                self.previous_throttle[axis] = self.throttle[axis]
                task_list.append(t)
        return task_list

    def throttle_value_list(self) -> list:
        return [self.throttle['x'], self.throttle['y'], self.throttle['z'],
                self.throttle['yaw'], self.throttle['roll']]

    def process_button(self, key: str, val):
        if "button_a" in key:
            self.previous_buttons['a'] = self.buttons['a']
            self.buttons['a'] = val
            if self.previous_buttons['a'] and not val:
                self.cameras.next_state()

    def axis_changed(self, axis: str) -> bool:
        if self.throttle[axis] == self.previous_throttle[axis]:
            debug("axis_update_verbose", "{} axis unchanged: {}",
                  [axis, self.throttle[axis]])
            return False
        else:
            debug("axis_update_verbose", "{} axis updated from {} to {}",
                  [axis, self.previous_throttle[axis], self.throttle[axis]])
            return True