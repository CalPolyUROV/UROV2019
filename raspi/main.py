"""Main Python code that runs on the robot and surface unit SBCs.

This python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary
between the Raspberry Pi on the surface unit and the Arduino/Teensy on the
robot. The scheduling module used in this program manages the serial and
sockets connections to the Arduino/Teensy and topside raspberry Pi
respectively.
"""
import sys

from snr.node import Node
from snr.utils.utils import print_exit, print_usage
from snr.context import root_context
import config

MODE_DEBUG = "debug"
MODE_DEPLOYED = "deployed"


def main():
    context = root_context()
    argc = len(sys.argv)
    if argc < 2:
        print_usage()
        print_exit("Improper usage")
    role = sys.argv[1]

    mode = MODE_DEPLOYED
    if "-d" in sys.argv:
        mode = MODE_DEBUG

    print(
        f"Starting {role} node in {mode} mode using Python {sys.version[0:5]}")

    node = None
    try:
        components = config.get(mode).get(role)
        node = Node(context, role, mode, components)
        node.loop()  # Blocking loop
    except KeyboardInterrupt:
        if node:
            context.log("framework", "Interrupted by user, exiting")
            node.set_terminate_flag("Interrupted by user")
        else:
            context.fatal("Exiting before node was done being constructed")
    finally:
        if node:
            node.terminate()
            node = None
    context.terminate()
    print_exit("Ya done now")


if __name__ == "__main__":
    main()
