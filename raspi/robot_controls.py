"""Perform calculations on controls data
determines axis of thrust and stores state information
"""

from typing import List

import settings
from robot_cameras import RobotCameras
from robot_motors import RobotMotors
from snr.task import SomeTasks
from snr.utils import Profiler, debug, init_dict

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
        -Camera switching
    Inputs TODO:
        -Mission tools
    """

    def __init__(self, profiler: Profiler):
        """Create data structures to hold implented data
        """
        self.cameras = RobotCameras(settings.NUM_ANALOG_CAMERAS)
        self.motor_control = RobotMotors(self.get_throttle_data, profiler)
        # Input data
        self.control_input = {}
        self.previous_cntl_input = {}

        # Internal data
        self.axis_list = ['x', 'y', 'z', "yaw", "roll"]
        self.previous_throttle = init_dict(self.axis_list, 0)
        self.throttle = init_dict(self.axis_list, 0)

        self.buttons_list = ['a']
        self.buttons = init_dict(self.buttons_list, False)
        self.previous_buttons = init_dict(self.buttons_list, False)
        # Pitch cannot be acheive with current motor configuration

    def get_throttle_data(self):
        return self.throttle

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

    def process_controls(self) -> SomeTasks:
        task_list = []
        # Collect only new control values
        debug("robot_control_verbose",
              "Processing controls data: {}", [self.control_input])
        for key in self.control_input.keys():
            # For each key that is incoming
            # if self.previous_cntl_input is not None:
            old_data = self.previous_cntl_input.get(key)
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
        if throttle_tasks is not None:
            task_list.append(throttle_tasks)
        if camera_tasks is not None:
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

    def get_throttle_tasks(self) -> SomeTasks:
        """Takes each throttle value and creates a task to send it to the MCU
        """
        debug("throttle_verbose", "Generating tasks for throttle values")
        s = "x:{}, y:{}, z:{}, yaw:{}, roll:{}"
        debug("throttle_values", s, self.throttle_value_list())

        # task_list = []
        # for axis in self.axis_list:
        #     if self.axis_changed(axis):
        #         t = Task(TaskType.serial_com, TaskPriority.high,
        #                  ["set_motor", axis, self.throttle[axis]])
        #         self.previous_throttle[axis] = self.throttle[axis]
        #         task_list.append(t)
        self.motor_control.update_motor_targets(self.get_throttle_data())
        task_list = self.motor_control.generate_serial_tasks()
        return task_list

    def throttle_value_list(self) -> List[int]:
        return [self.throttle['x'], self.throttle['y'], self.throttle['z'],
                self.throttle['yaw'], self.throttle['roll']]

    def process_button(self, key: str, val):
        if "button_a" in key:
            self.store_button('a', val)
            if self.button_pressed('a'):
                pass
            elif self.button_released('a'):
                self.cameras.next_state()

        elif "button_b" in key:
            self.store_button('b', val)
            if self.button_pressed('b'):
                pass
            elif self.button_released('b'):
                pass
        elif "button_x" in key:
            self.store_button('x', val)
            if self.button_pressed('x'):
                pass
            elif self.button_released('x'):
                pass
        elif "button_y" in key:
            self.store_button('y', val)
            if self.button_pressed('y'):
                pass
            elif self.button_released('y'):
                pass

    def store_button(self, button: str, val: bool):
        self.previous_buttons[button] = self.buttons.get(button)
        self.buttons[button] = val

    def button_pressed(self, button: str):
        # Button is pressed and was previous not pressed
        return self.buttons[button] and not self.previous_buttons[button]

    def button_released(self, button: str):
        # Button was previous pressed but is now released
        return self.previous_buttons[button] and not self.buttons[button]

    def axis_changed(self, axis: str) -> bool:
        if self.throttle[axis] == self.previous_throttle[axis]:
            debug("axis_update_verbose", "{} axis unchanged: {}",
                  [axis, self.throttle[axis]])
            return False
        else:
            debug("axis_update_verbose", "{} axis updated from {} to {}",
                  [axis, self.previous_throttle[axis], self.throttle[axis]])
            return True
