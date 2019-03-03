"""Reads controller data for topside 
Based on example controller code from https://www.pygame.org/docs/ref/joystick.html
"""
# Sytem imports
import pygame
import _thread
from typing import Callable
import random

# Our imports
import settings
from snr import Source
from utils import debug, try_key, sleep


class Controller(Source):
    def __init__(self, name: str, store_data: Callable):
        if not settings.USE_CONTROLLER:
            debug("controller", "Controller disabled by settings")
            return

        super().__init__(name, self.monitor_controller, settings.CONTROLLER_TICK_RATE)

        self.store_data = store_data
        self.init_controller()
        self.loop()

    def init_controller(self):
        if not settings.SIMULATE_INPUT:
            pygame.init()  # Initialize pygame
            pygame.joystick.init()  # Initialize the joysticks
        # TODO: Require the user to zero each trigger by depressing it and
        # releasing it. This is necessary because the triggers start at 50
        # and are only zeroed after the initial press and release.

    def monitor_controller(self):
        if settings.SIMULATE_INPUT:
            debug("controller_event", "Simulating input")
            joystick_data = simulate_input()
        else:
            debug("controller_verbose", "Reading input")
            joystick_data = self.read_joystick()
        controls_dict = self.map_input_dict(joystick_data)

        debug("controller_event",
              "Storing data with key: {}", [self.get_name()])
        debug("controller_verbose",
              "\n\tController data:\n\t {}", [controls_dict])
        self.store_data(self.get_name(), controls_dict)

    def print_data(self, d: dict):
        for val in self.joystick_data:
            print(str(val) + ":\t" + str(self.joystick_data[val]))

    def map_input_dict(self, joystick_data: dict) -> dict:
        """Convert pygame input names to our names based off settings
        """
        control_data = {}
        for k in joystick_data.keys():
            (new_key, new_value) = self.map_input(k, joystick_data[k])
            if new_key != None:
                control_data[new_key] = new_value
        return control_data

    def map_input(self, key: str, value):
        """Maps an individual KV pair to our controls
        """
        map_list = try_key(settings.control_mappings, key)

        new_key = map_list[0]

        if value is tuple:
            debug("control_mappings", "Unwrapping tuple {}", [value])
            value = value[0]

        if value is str:
            debug("control_mappings", "Control value is str {}", [value])
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

        debug("control_mappings_verbose", "Mapped value {}", [value])
        try:
            key_val_tuple = (new_key, value)
        except Exception as error:
            debug("control_mappings", "Error: {}", [error.__repr__()])
            exit("Fatalityyyy")

        return key_val_tuple

    def cast(self, value: object, t: type)-> object:
        if t is None:
            return value
        elif t is int:
            return int(value)
        elif t is bool:
            return value != 0
        elif t is tuple:
            if value is tuple:
                return value
            elif value.__class__ is float:
                return (int((value * 4) - 2), int((value * - 4) + 2))
            else:
                debug("control_mappings_verbose", "Trying to cast {}: {} as tuple", [value.__class__, value])
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
        # Get the index of which joystick in the event that multiple are connected
        joystick_data["number"] = i
        # Get the name from the OS for the controller/joystick
        joystick_data["name"] = joystick.get_name()

        # Enumerate number floating point values
        joystick_data["num_axes"] = joystick.get_numaxes()
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

        return joystick_data

    def terminate(self):
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        debug("controls_reader_verbose", "exiting pygame")
        settings.USE_CONTROLLER = False
        pygame.quit()
        debug("controls_reader", "exited pygame")
        self.set_terminate_flag()


def random_val():
    """Generates random values for simulated control input
    """
    # TODO: Account for different kinds of input data such as joysticks vs buttons
    return random.random()


def simulate_input() -> dict:
    """Provide fake input values for testing purposes
    """
    # debug("simulation", "Simulating control input")
    sim_data = {}
    for key in settings.control_mappings.keys():
        # key = settings.control_mappings[k][0]
        # if not key == None:
        # debug("simulation_verbose", "Adding key {}", [key])
        sim_data[key] = random_val()
        # TODO: provide specific data types for relevent keys
    debug("simulation", "Simulated control input was applied")
    debug("simulation_verbose", "Simulated control input:\n{}", [sim_data])
    return sim_data


# def format_controls(data: dict) -> dict:
#     # Only pass control values that are not zrero
#     new_data = {}
#     for k in data:
#         if data[k] != 0:
#             new_data[k] = data[k]
#     return new_data
