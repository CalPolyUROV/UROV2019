"""Reads controller data for topside
Based on example controller code from
https://www.pygame.org/docs/ref/joystick.html
"""

import random
from typing import Tuple, Union

import pygame

import settings
from snr.async_endpoint import AsyncEndpoint
from snr.node import Node
from snr.task import SomeTasks


class Controller(AsyncEndpoint):
    def __init__(self, parent: Node,
                 name: str):
        if not settings.USE_CONTROLLER:
            self.dbg("controller", "Controller disabled by settings")
            # This early return might break things
            return
        self.task_producers = []
        self.task_handlers = {}

        super().__init__(parent, name,
                         self.init_controller,
                         self.monitor_controller,
                         settings.CONTROLLER_INIT_TICK_RATE)

        self.datastore = self.parent.datastore

        # Require triggers to be set to zero before operation
        # Initial value is inverse of setting
        # Triggers zerod indicated whether the triggers no longer need to be
        # zeroed
        self.triggers_zeroed = not settings.CONTROLLER_ZERO_TRIGGERS
        self.joystick_data = {}

        self.start_loop()

    def store_data(self, data):
        # self.dbg("controller", "taking in data")
        self.datastore.store(self.name, data)

    def init_controller(self):
        if settings.SIMULATE_INPUT:
            s = "Simulating input without pygame and XBox controller"
            self.dbg("controller_event", s)
            self.triggers_zeroed = True
            return
        import pygame
        pygame.init()  # Initialize pygame
        pygame.joystick.init()  # Initialize the joysticks
        pygame.event.get()
        num_controllers = pygame.joystick.get_count()

        if num_controllers > 0:
            self.dbg("controller", "Controllers found: {}", [num_controllers])
            print_controller_warning()
            # TODO: Handle pygame's segfault when the controller disconnects
        elif settings.REQUIRE_CONTROLLER:
            s = "Controller required by settings, {} found"
            self.dbg("controller_error", s, [num_controllers])
            exit("Required XBox controller absent")
        else:
            s = "Controller not found but not required, simulating input"
            self.dbg("controller", s)
            settings.SIMULATE_INPUT = True
            return

    def monitor_controller(self):
        if settings.SIMULATE_INPUT:
            self.dbg("controller_event", "Simulating input")
            joystick_data = self.simulate_input()
        else:
            # if not pygame.joystick.get_init():

            self.dbg("controller_verbose", "Reading input")
            try:
                num_controllers = pygame.joystick.get_count()
                if num_controllers < 1:
                    raise pygame.error
                joystick_data = self.read_joystick()
            except pygame.error as error:
                self.dbg("controller_error", "Controller error: {}",
                         [error.__repr__()])
                if not settings.REQUIRE_CONTROLLER:
                    self.dbg(
                        "controller_error",
                        "Missing controller not required, simulating input")
                    joystick_data = simulate_input()
                else:
                    self.dbg("controller_error",
                             "Lost connection to controller, {} found",
                             [num_controllers])
                    raise Exception("Lost connection to controller")
        new_data = self.map_input_dict(joystick_data)
        controls_dict = self.check_trigger_zeroed(new_data)

        self.dbg("controller_event",
                 "Storing data with key: {}", [self.get_name()])
        self.dbg("controller_verbose",
                 "\n\tController data:\n\t {}", [controls_dict])
        self.store_data(controls_dict)

    def print_data(self, d: dict):
        for val in d:
            print(str(val) + ":\t" + str(d[val]))

    def check_trigger_zeroed(self, data: dict):
        if self.triggers_zeroed:
            return data
        left = data.get("trigger_left")
        right = data.get("trigger_right")

        if ((left == 0) and (right == 0)) or settings.SIMULATE_INPUT:
            self.triggers_zeroed = True
            self.set_delay(settings.CONTROLLER_TICK_RATE)
            self.dbg("controller",
                     "Triggers successfully zeroed. Controller ready.")
            return data

        self.dbg("controller_error",
                 "Please zero triggers: left: {}, right: {}",
                 [left, right])
        return {}

    def map_input_dict(self, joystick_data: dict) -> dict:
        """Convert pygame input names to our names based off settings
        """
        control_data = {}
        for k in joystick_data.keys():
            (new_key, new_value) = self.map_input(k, joystick_data[k])
            if new_key is not None:
                control_data[new_key] = new_value
        return control_data

    def map_input(self, key: str, value) -> Tuple:
        """Maps an individual KV pair to our controls
        """
        map_list = settings.control_mappings.get(key)

        if not isinstance(map_list, list):
            return key, value

        new_key = map_list[0]

        if value is tuple:
            self.dbg("control_mappings", "Unwrapping tuple {}", [value])
            value = value[0]

        if value is str:
            self.dbg("control_mappings", "Control value is str {}", [value])
            exit("Stringtalityyy")

        t = None
        if len(map_list) > 1:
            t = map_list[1]
        if len(map_list) > 2:
            scale_factor = map_list[2]
            value = value * scale_factor
        if len(map_list) > 3:
            shift_ammount = map_list[3]
            value = value + shift_ammount
        if len(map_list) > 4:
            dead_zone = map_list[4]
            if abs(value) < dead_zone:
                # value is inside dead zone
                value = 0
        value = self.cast(value, t)

        self.dbg("control_mappings_verbose", "Mapped value {}", [value])
        try:
            key_val_tuple = (new_key, value)
        except Exception as error:
            self.dbg("control_mappings", "Error: {}", [error.__repr__()])
            exit("Fatalityyyy")

        return key_val_tuple

    def cast(self, value, t: Union[type, None]):
        if t is None:
            return value
        if t is int:
            return int(value)
        if t is bool:
            return value != 0
        if t is tuple:
            if value is tuple:
                return value
            if isinstance(value, float):
                return (int((float(value) * 4) - 2),
                        int((float(value) * -4) + 2))
            self.dbg("control_mappings_verbose",
                     "Trying to cast {}: {} as tuple", [
                         type(value), value])
        return value

    def read_joystick(self) -> dict:
        """Function run in separate thread to update control data
        Updates instance variable without using main thread CPU time
        """
        if (not settings.USE_CONTROLLER) or settings.SIMULATE_INPUT:
            return {}

        pygame.event.get()

        # Get count of joysticks
        i = pygame.joystick.get_count() - 1

        joystick_data = {}

        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        # Get the index of which joystick if there are multiple connected
        joystick_data["number"] = i
        # Get the name from the OS for the controller/joystick
        # joystick_data["name"] = joystick.get_name()

        # Enumerate number floating point values
        joystick_data["num_axes"] = joystick.get_numaxes()

        # some bs to get another axes for windows
        if joystick.get_numaxes() == 5:
            joystick_data["axis_0"] = joystick.get_axis(0)
            joystick_data["axis_1"] = joystick.get_axis(1)
            if joystick.get_axis(2) > 0.000001:
                joystick_data["axis_2"] = joystick.get_axis(2)
            else:
                joystick_data["axis_2"] = 0
            joystick_data["axis_3"] = joystick.get_axis(3)
            joystick_data["axis_4"] = joystick.get_axis(4)
            if joystick.get_axis(2) < -0.000001:
                joystick_data["axis_5"] = -joystick.get_axis(2)
            else:
                joystick_data["axis_5"] = 0
        else:
            for i in range(joystick_data["num_axes"]):
                joystick_data["axis_" + str(i)] = joystick.get_axis(i)

        # Enumerate number of buttons
        joystick_data["num_buttons"] = joystick.get_numbuttons()
        for i in range(joystick_data["num_buttons"]):
            joystick_data["button_" +
                          str(i)] = joystick.get_button(i)
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        joystick_data["num_dpad"] = joystick.get_numhats()
        for j in range(joystick_data["num_dpad"]):
            joystick_data["dpad"] = joystick.get_hat(j)

        self.dbg("controls_reader_verbose",
                 "{}",
                 [joystick_data])
        return joystick_data

    def terminate(self):
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        if(not settings.SIMULATE_INPUT):
            self.dbg("controls_reader_verbose",
                     "exiting pygame")
            settings.USE_CONTROLLER = False
            pygame.quit()
            self.dbg("controls_reader",
                     "Exited pygame")
        else:
            self.dbg("controls_reader_verbose",
                     "Closing simulated controller")

    def simulate_input(self) -> dict:
        """Provide fake input values for testing purposes
        Correct data types for key values are transformed to in map_input
        """
        self.dbg("simulation",
                 "Simulating control input")
        sim_data = {}
        for key in settings.control_mappings:
            self.dbg("simulation_verbose",
                     "Simulating key: {}",
                     [key])
            sim_data[key] = random_val()
        self.dbg("simulation_verbose",
                 "Simulated control input:\n{}",
                 [sim_data])
        return sim_data


def random_val():
    """Generates random values for simulated control input
    All values are floats between 0.0 and 1.0. These are transformed
    to the correct data type in map_input
    """
    return random.random()


def print_controller_warning():
    s = "Warning: disconnecting the controller will crash the topside program"
    print(s)
