#!/usr/bin/python3.5
""" Main Python code that runs on the Raspberry Pi 3 B+ inside the robot and surface unit

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

# System imports
import sys  # For command line arguments

# Scheduling imports
import settings
from robot import Robot
from snr import Node, Scheduler
from topside import Topside
from utils import debug, exit, sleep, print_usage

def main():
    if len(sys.argv) < 2:
        print_usage()
        exit("Improper usage, consider launching from the Makefile with 'make server' and 'make'")

    settings.ROLE = sys.argv[1]  # Command line argument

    if settings.ROLE.__eq__("robot"):
        debug("framework", "Running as robot")
        node = Robot()
    elif settings.ROLE.__eq__("topside"):
        debug("framework", "Running as server")
        node = Topside()
    else:
        debug("framework", "Invalid ROLE {} given as command line arg", [
            settings.ROLE])
        print_usage()
        exit("Unknown ROLE")

    try:
        node.loop()
    except KeyboardInterrupt:
        print()
        debug("framework", "Interrupted by user, exiting")

    node.terminate()
    debug("framework", "Node terminated")
    exit("Ya done now")

if __name__ == "__main__":
    main()
