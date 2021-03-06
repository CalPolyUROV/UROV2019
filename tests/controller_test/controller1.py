"""Example controller code from https://www.pygame.org/docs/ref/joystick.html
"""

import pygame
import _thread

# Mapping of pygame joystick output to values we can make sense of
# "pygame_name":"name_we_use",
control_mappings = {"number": "controller_num",
                    "name": "controler_name",
                    "axis_0": "axis_0",
                    "axis_1": "axis_1",
                    "axis_2": "axis_2",
                    "axis_3": "axis_3",
                    "axis_4": "axis_4",
                    "axis_5": "axis_5",
                    "axis_1": "axis_1",
                    "button_0": "button_a",
                    "button_1": "button_b",
                    "button_2": "button_x",
                    "button_3": "button_y",
                    "button_4": "button_4",
                    "button_5": "button_5",
                    "button_6": "button_6",
                    "button_7": "button_7",
                    "button_8": "button_8",
                    "button_9": "button_9",
                    "dpad": "dpad"
                    }


class Controller:

    def __init__(self):
        self.joystick_data = {}
        self.data_number = 0
        _thread.start_new_thread(self.initialize, ())

    def print_data(self, d: dict):
        for val in self.joystick_data:
            print(str(val) + ":\t" + str(self.joystick_data[val]))

    def get_input(self):
        print("Data number: " + str(self.data_number))
        self.print_data(self.joystick_data)
        self.data_number = self.data_number + 1
        return self.map_data(self.joystick_data)

    def map_data(self, joystick_data: dict) -> dict:
        control_data = {}
        for k in joystick_data:
            control_data[self.try_key(control_mappings, k)] = joystick_data[k]
        return control_data

    def try_key(self, d: dict, k: str):
        try:
            return d[k]
        except (KeyError):
            return "Key not supplied in mapping: " + k

    def initialize(self):
        pygame.init()
        # Loop until the user clicks the close button.
        done = False
        # Initialize the joysticks
        pygame.joystick.init()
        while not done:
            # EVENT PROCESSING STEP
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

                self.joystick_data["num_axes"] = joystick.get_numaxes()
                for i in range(self.joystick_data["num_axes"]):
                    self.joystick_data["axis_" + str(i)] = joystick.get_axis(i)

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
        pygame.quit()
