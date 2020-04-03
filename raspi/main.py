"""Main Python code that runs on the Raspberry Pi on robot and surface unit.

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary
between the Raspberry Pi on the surface unit and the Arduino/Teensy on the
robot. The scheduling module used in this program manages the serial and
sockets connections to the Arduino/Teensy and topside raspberry Pi
respectively.
"""
import sys

from snr.node import Node
from snr.utils.utils import print_exit, print_usage
from snr.debug import Debugger
import config

context = "framework_main"


def main():
    argc = len(sys.argv)
    if argc < 2:
        print_usage()
        print_exit("Improper usage")
    role = sys.argv[1]

    mode = "deployed"
    if "-d" in sys.argv:
        mode = "debug"

    print("Starting {} node in {} mode using Python {}".format(
        role, mode, sys.version[0:5]))

    debugger = Debugger()
    dbg = debugger.debug

    node = None
    try:
        components = config.get_components(role, mode)
        node = Node(debugger, role, mode, components)
        node.loop()  # Blocking loop
    except KeyboardInterrupt:
        dbg("framework", "Interrupted by user, exiting")
        if node:
            node.set_terminate_flag("Interrupted by user")
        else:
            dbg(context, "Exiting before node was done being constructed")

    if node:
        node.terminate()
        node = None
    debugger.join()
    print_exit("Ya done now")


if __name__ == "__main__":
    main()
