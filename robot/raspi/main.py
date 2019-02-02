#!/usr/bin/python3.5
""" Main Python code that runs on the Raspberry Pi 3 B+ inside the robot and surface unit

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary between the Raspberry Pi on
the surface unit and the Arduino/Teensy on the robot. The scheduling module
used in this program manages the serial and sockets connections to the
Arduino/Teensy and topside raspberry Pi respectively.
"""

# System imports
from sys import argv  # For command line arguments

# Scheduling imports
import settings
from robot import Robot
from snr import Node, Scheduler
from topside import Topside
from utils import debug, exit, sleep, print_usage, switch


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()
        exit("Improper usage, consider launching from the Makefile with 'make server' or 'make robot'")

    role = argv[1]  # Command line argument
    mode = "deployed"

    if "-d" in argv:
        mode = "debug"

    role = argv[1]
    if role.__eq__("robot"):
        debug("framework", "Running as robot")
        node = Robot(mode)
    elif role.__eq__("topside"):
        debug("framework", "Running as server")
        node = Topside(mode)
    else:
        debug("framework", "Invalid ROLE {} given as command line arg", [role])
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
