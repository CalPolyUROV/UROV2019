"""Reads controller data for topside 
Based on example controller code from https://www.pygame.org/docs/ref/joystick.html
"""
# Sytem imports
import pygame
import _thread

# Our imports
import settings
from utils import debug, random_val, try_key

class Controller:
    def __init__(self):
        self.joystick_data = {}
        if settings.USE_CONTROLLER:
            # Split constant controller readings to new thread
            _thread.start_new_thread(self.initialize, ())
        else:
            debug("controller", "Controller disabled by settings")

    def print_data(self, d: dict):
        for val in self.joystick_data:
            print(str(val) + ":\t" + str(self.joystick_data[val]))

    def get_input(self):
        """Get mapped input data from instance variable
        """
        if not settings.SIMULATE_INPUT:
            return self.map_input_dict(self.joystick_data)
        else:
            return simulate_input()

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
        
        if len(map_list) > 1:
            # Use scale_factor
            value = value * map_list[1]
        if len(map_list) > 2:
            # Use shift_ammount
            value = value + map_list[2]
        if len(map_list) > 3:
            # Use dead_zone
            if abs(value) < map_list[3]:
                # value is inside dead zone
                value = 0
        return (map_list[0], value)


    def initialize(self):
        """Function run in separate thread to update control data
        Updates instance variable without using main thread CPU time
        """
        if settings.SIMULATE_INPUT:
            # Shortcircuit and exit thread if actual input will not be used
            return
        pygame.init()  # Initialize pygame
        done = False

        pygame.joystick.init()  # Initialize the joysticks
        while not done:

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

            # For each joystick:
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                # Get the index of which joystick in the event that multiple are connected
                self.joystick_data["number"] = i
                # Get the name from the OS for the controller/joystick
                self.joystick_data["name"] = joystick.get_name()

                # Enumerate number floating point values
                self.joystick_data["num_axes"] = joystick.get_numaxes()
                for i in range(self.joystick_data["num_axes"]):
                    self.joystick_data["axis_" + str(i)] = joystick.get_axis(i)

                # Enumerate number of buttons
                self.joystick_data["num_buttons"] = joystick.get_numbuttons()
                for i in range(self.joystick_data["num_buttons"]):
                    self.joystick_data["button_" +
                                       str(i)] = joystick.get_button(i)
                # Hat switch. All or nothing for direction, not like joysticks.
                # Value comes back in an array.
                self.joystick_data["num_dpad"] = joystick.get_numhats()
                for i in range(self.joystick_data["num_dpad"]):
                    self.joystick_data["dpad"] = joystick.get_hat(i)

    def close():
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        debug("controls_reader", "exiting pygame")
        pygame.quit()
        debug("controls_reader", "exited pygame")


def simulate_input() -> dict:
    """Provide fake input values for testing purposes
    """
    # debug("simulation", "Simulating control input")
    sim_data = {}
    for k in settings.control_mappings:
        key = settings.control_mappings[k]
        if not key == None:
            # debug("simulation_verbose", "Adding key {}", [key])
            sim_data[key] = random_val()
            # TODO: provide specific data types for relevent keys
    debug("simulation", "Simulated control input was applied")
    debug("simulation_verbose", "Simulated control input:\n{}", [sim_data])
    return sim_data


def format_controls(data: dict) -> dict:
    # Only pass control values that are not zrero
    new_data = {}
    for k in data:
        if data[k] != 0:
            new_data[k] = data[k]
    return new_data
