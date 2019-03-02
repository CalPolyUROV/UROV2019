"""Reads controller data for topside 
Based on example controller code from https://www.pygame.org/docs/ref/joystick.html
"""
# Sytem imports
import pygame
import _thread
from typing import Callable

# Our imports
import settings
from snr import Source
from utils import debug, random_val, try_key, sleep


class Controller(Source):
    def __init__(self, name: str, store_data: Callable):
        if not settings.USE_CONTROLLER:
            debug("controller", "Controller disabled by settings")
            return

        super().__init__(name, self.monitor_controller, settings.CONTROLLER_TICK_RATE)

        self.store_data = store_data

        self.loop()

    def init_controller(self):
        if not settings.SIMULATE_INPUT:
            pygame.init()  # Initialize pygame
            pygame.joystick.init()  # Initialize the joysticks

    def monitor_controller(self):
        if settings.SIMULATE_INPUT:
            debug("controller_verbose", "Simulating input")
            controls_dict = simulate_input()
        else:
            debug("controller_verbose", "Reading input")
            joystick_data = self.read_joystick()
            controls_dict = self.map_input_dict(self.joystick_data)

        debug("controller", "Storing data with key: {}", [super().get_name()])
        debug("controller_verbose", "Data: {}", [controls_dict])
        self.store_data(super().get_name(), controls_dict)

    def print_data(self, d: dict):
        for val in self.joystick_data:
            print(str(val) + ":\t" + str(self.joystick_data[val]))

    def map_input_dict(self, joystick_data: dict) -> dict:
        """Convert pygame input names to our names based off settings
        """
        control_data = {}
        for k in joystick_data:
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

        if len(map_list) > 1:
            scale_factor = map_list[1]
            value = value * scale_factor
        if len(map_list) > 2:
            shift_ammount = map_list[2]
            value = value + shift_ammount
        if len(map_list) > 3:
            dead_zone = map_list[3]
            if abs(value) < dead_zone:
                # value is inside dead zone
                value = 0
        if value is int:
            value = int(round(value))

        debug("control_mappings_verbose", "Mapped value {}", [value])
        try:
            key_val_tuple = (new_key, value)
        except Exception as error:
            debug("control_mappings", "Error: {}", [error.__repr__()])
            exit("Fatalityyyy")

        return key_val_tuple

    def read_joystick(self) -> dict:
        """Function run in separate thread to update control data
        Updates instance variable without using main thread CPU time
        """

        # TODO: Investigate whether this part of the loop is necessary
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                # print("Joystick button pressed.")
                pass
            if event.type == pygame.JOYBUTTONUP:
                # print("Joystick button released.")
                pass

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        joystick_data = {}

        # For each joystick:
        for i in range(joystick_count):
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
            for i in range(joystick_data["num_dpad"]):
                joystick_data["dpad"] = joystick.get_hat(i)
        return joystick

    def terminate(self):
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        debug("controls_reader_verbose", "exiting pygame")
        pygame.quit()
        debug("controls_reader", "exited pygame")
        super().set_terminate_flag()


def simulate_input() -> dict:
    """Provide fake input values for testing purposes
    """
    # debug("simulation", "Simulating control input")
    sim_data = {}
    for k in settings.control_mappings:
        key = settings.control_mappings[k][0]
        if not key == None:
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
