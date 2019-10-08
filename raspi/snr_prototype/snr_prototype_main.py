from sys import argv

from snr_lib import Node
from snr_utils import debug, print_usage, u_exit


from snr_prototype.snr_prototype_factories import *


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()
        u_exit("Improper usage")
    device_selection = str(argv[1])

    mode = "deployed"
    if "-d" in argv:
        mode = "debug"

    # Connections between devices
    controls_link = EthernetLink(9230, 9131, "controls_data")
    telemetry_link = EthernetLink(9120, 9121, "telemetry_data")
    serial_link = SerialFactory("motor_data", "sensor_data",
                                "path_to_arduino_program")

    if device_selection is "robot":
        components = [controls_link.client,
                      telemetry_link.server,
                      RobotControlsFactory("controls_data", "thruster_data"),
                      RobotMotorsFactory("thruster_data", "motors_data"),
                      serial_link]

    elif device_selection is "topside":
        components = [controls_link.server,
                      telemetry_link.client,
                      ControllerFactory("controls_data")]

    node = Node(components)

    node.start()
