#!/usr/bin/python3.6
""" Main Python code that runs on the Raspberry Pi 3B inside the robot

This is the python program is meant to run on the Raspberry Pi located on
the robot. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

# Scheduling imports
import settings
from schedule import Schedule, Task
from utils import sleep, exit


def main():
    settings.ROLE = "robot"
    # settings.PRINTING = False

    # Make a schedule object
    s = Schedule()

    # This  initializes the sockets/networking code
    # Note: The sockets should not connect to the topside unit until after the
    #   serial connection has been made.
    #   (This is arbitrary, but the reasoning is that the robot should enumerate
    #   its own pieces prior to connecting to the server)
    #   (however the serial connection uses a handshake/"est_con")
    s.schedule_initial_tasks()

    seq_num_val = 0
    terminate = False  # Whether to exit main loop
    while not terminate:
        # Get new tasks if needed
        # TODO: Integrate this if statement into the get_new_tasks call or a check_for_new_tasks()
        if not s.has_tasks():
            s.get_new_tasks()

        # Get the next task to execute
        t = s.get_next_task()
        s.execute_task(t, seq_num_val)
        seq_num_val += 1
        # sleep(2)  # Temporary delay to not make things too fast during testing

    s.terminate()


# https://stackoverflow.com/questions/21120947/catching-keyboardinterrupt-in-python-during-program-shutdown
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit("Interrupted, exiting")
