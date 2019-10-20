"""Main Python code that runs on the Raspberry Pi on robot and surface unit.

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary
between the Raspberry Pi on the surface unit and the Arduino/Teensy on the
robot. The scheduling module used in this program manages the serial and
sockets connections to the Arduino/Teensy and topside raspberry Pi
respectively.
"""
from sys import argv

import settings
from robot_controls import RobotControlsFactory
from snr.comms.serial.factory import SerialFactory
from snr.comms.sockets.factory import EthernetLink
from snr.io.controller.factory import ControllerFactory
from snr.node import Node
from snr.utils import debug, print_exit, print_mode, print_usage


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()
        print_exit("Improper usage")
    role = str(argv[1])

    print_mode(role)

    mode = "deployed"
    if "-d" in argv:
        mode = "debug"

    # Connections between devices
    controls_link = EthernetLink(settings.CONTROLS_SOCKETS_CONFIG.port,
                                 settings.CONTROLS_DATA_NAME)
    telemetry_link = EthernetLink(settings.TELEMETRY_SOCKETS_CONFIG.port,
                                  settings.TELEMETRY_DATA_NAME)
    serial_link = SerialFactory("motor_data", "sensor_data",
                                "path_to_arduino_program")

    # Controls and motor processing
    robot_controls = RobotControlsFactory(settings.CONTROLS_DATA_NAME,
                                          "thruster_data")

    # XBox Controller
    controller = ControllerFactory(settings.CONTROLS_DATA_NAME)

    components = []
    if role.__eq__("robot"):
        components = [controls_link.client,
                      #   telemetry_link.server,
                      robot_controls,
                      serial_link]

    elif role.__eq__("topside"):
        components = [controls_link.server,
                      #   telemetry_link.client,
                      controller]

    node = Node(role, mode, components)
    # Run the node's loop
    try:
        node.loop()
    except KeyboardInterrupt:
        print()
        debug("framework", "Interrupted by user, exiting")

    node.terminate()
    debug("framework", "Node terminated")
    print_exit("Ya done now")


if __name__ == "__main__":
    main()
