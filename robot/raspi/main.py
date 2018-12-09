#!/usr/bin/python3.6
""" Main Python code that runs on the Raspberry Pi 3B inside the robot

This is the python program is meant to run on the Raspberry Pi located on
the robot. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

# System imports
import sys  # For command line arguments

# Scheduling imports
import settings
from schedule import Schedule, Node
from utils import sleep, exit, debug, debug_f
from robot import Robot
from topside import Topside


def main():
    settings.ROLE = sys.argv[1]  # Command line argument

    if settings.ROLE == "robot":
        node = Robot()
    elif settings.ROLE == "topside":
        node = Topside()
    else:
        debug_f("framework", "Invalid ROLE {} given as command line arg", [settings.ROLE])
        exit("Unknown ROLE")

    node.loop()
    node.terminate()

if __name__ == "__main__":
    # https://stackoverflow.com/questions/21120947/catching-keyboardinterrupt-in-python-during-program-shutdown
    try:
        main()
    except KeyboardInterrupt:
        exit("Interrupted, exiting")
