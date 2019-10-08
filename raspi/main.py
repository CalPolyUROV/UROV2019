""" Main Python code that runs on the Raspberry Pi on robot and surface unit

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary
between the Raspberry Pi on the surface unit and the Arduino/Teensy on the
robot. The scheduling module used in this program manages the serial and
sockets connections to the Arduino/Teensy and topside raspberry Pi
respectively.
"""
from sys import argv

from snr.utils import debug, print_usage, u_exit, print_mode
from snr.factory import *
from snr.node import Node
from robot_controls import RobotControlsFactory


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()
        u_exit("Improper usage")
    device_selection = str(argv[1])

    print_mode(device_selection)

    mode = "deployed"
    if "-d" in argv:
        mode = "debug"

    # Connections between devices
    controls_link = EthernetLink(9230, 9131, "controls_data")
    telemetry_link = EthernetLink(9120, 9121, "telemetry_data")
    serial_link = SerialFactory("motor_data", "sensor_data",
                                "path_to_arduino_program")

    # Controls and motor processing
    robot_controls = RobotControlsFactory("controls_data", "thruster_data")
    robot_motors = RobotMotorsFactory("thruster_data", "motors_data")

    # XBox Controller
    controller = ControllerFactory("controls_data")
    components = []
    if device_selection.__eq__("robot"):
        components = [controls_link.client,
                      telemetry_link.server,
                      robot_controls,
                      robot_motors,
                      serial_link]

    elif device_selection.__eq__("topside"):
        components = [controls_link.server,
                      telemetry_link.client,
                      controller]

    node = Node(mode, components)
    # Run the node's loop
    try:
        node.loop()
    except KeyboardInterrupt:
        print()
        debug("framework", "Interrupted by user, exiting")

    node.terminate()
    debug("framework", "Node terminated")
    u_exit("Ya done now")


if __name__ == "__main__":
    main()
