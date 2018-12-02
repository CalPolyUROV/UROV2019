"""Example controller code from https://www.pygame.org/docs/ref/joystick.html
"""

import pygame
import _thread


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
        control_data["controller_num"] = self.try_key(joystick_data, "number")
        control_data["controller_name"] = self.try_key(joystick_data, "name")
        control_data["axis_1"] = self.try_key(joystick_data, "axis_1")
        control_data["axis_2"] = self.try_key(joystick_data, "axis_2")
        control_data["axis_3"] = self.try_key(joystick_data, "axis_3")
        control_data["axis_4"] = self.try_key(joystick_data, "axis_4")
        control_data["button_a"] = self.try_key(joystick_data, "button_0")
        control_data["button_b"] = self.try_key(joystick_data, "button_1")
        control_data["button_x"] = self.try_key(joystick_data, "button_2")
        control_data["button_y"] = self.try_key(joystick_data, "button_3")
        control_data["button_4"] = self.try_key(joystick_data, "button_4")
        control_data["button_5"] = self.try_key(joystick_data, "button_5")
        control_data["button_6"] = self.try_key(joystick_data, "button_6")
        control_data["button_7"] = self.try_key(joystick_data, "button_7")
        control_data["button_8"] = self.try_key(joystick_data, "button_8")
        control_data["button_9"] = self.try_key(joystick_data, "button_9")
        control_data["dpad"] = self.try_key(joystick_data, "dpad")
        return control_data

    def try_key(self, d: dict, k: str):
        try:
            return d[k]
        except (KeyError):
            return "Key invalid: " + k

    def initialize(self):

        pygame.init()

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        # clock = pygame.time.Clock()

        # Initialize the joysticks
        pygame.joystick.init()

        # -------- Main Program Loop -----------
        while done == False:
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

            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

            # # Go ahead and update the screen with what we've drawn.
            # pygame.display.flip()

            # # Limit to 20 frames per second
            # clock.tick(20)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
