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
from snr.camera.factory import CameraManagerPair
from snr.comms.serial.factory import SerialFactory
from snr.comms.sockets.factory import EthernetLink
from snr.io.controller.factory import ControllerFactory
from snr.zynq.factory import ZyboFactory
from snr.node import Node
from snr.utils.utils import print_exit, print_mode, print_usage
from snr.debug import Debugger
from ui.gui.factory import GUIFactory


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

    debugger = Debugger()
    dbg = debugger.debug

    # Connections between devices
    # Ethernet tether link for control data
    controls_link = EthernetLink(settings.CONTROLS_SOCKETS_CONFIG.port,
                                 settings.CONTROLS_DATA_NAME)
    # Ethernet tether link for telemetry data
    telemetry_link = EthernetLink(settings.TELEMETRY_SOCKETS_CONFIG.port,
                                  settings.TELEMETRY_DATA_NAME)
    # Controls and motor processing
    robot_controls = RobotControlsFactory(settings.CONTROLS_DATA_NAME,
                                          "thruster_data")
    # GUI
    GUI = GUIFactory([settings.CONTROLS_DATA_NAME,
                      settings.TELEMETRY_DATA_NAME])
    # XBox Controller
    # Zynq Zybo Z7-20: replaces serial link
    zynq_link = ZyboFactory("motor_data", "sensor_data")
    controller = ControllerFactory(settings.CONTROLS_DATA_NAME)
    # UART/USB link to Arduino for motor control and sensor reading
    serial_link = SerialFactory("motor_data", "sensor_data",
                                "path_to_arduino_program(unimplemented)")
    # Cameras
    cameras = CameraManagerPair({
        # "main_camera0": 0,
        # "ir_camera1": 1,
        # "ir_camera2": 2,
        # "ir_camera3": 3,
        # "usb_camera4": 4,
        # "ir_camera5": 5,
        # "usb_camera6": 6,
        # "ir_camera7": 7,
        # "usb_camera8": 8,
        # "usb_camera9": 9,
        # "usb_camera10": 10,
        # "usb_camera10": 11,
        # "usb_camera10": 12,
    })

    components = []
    if role.__eq__("topside"):
        components = [controls_link.server,
                      telemetry_link.client,
                      controller,
                      GUI,
                    #   cameras.receiver
                      ]
    elif role.__eq__("robot"):
        components = [controls_link.client,
                      telemetry_link.server,
                      robot_controls,
                      serial_link,
                    #   cameras.source
                      ]
    elif role.__eq__("zybo"):
        components = [controls_link.client,
                      telemetry_link.server,
                      robot_controls,
                      zynq_link
                      ]

    node = Node(debugger, role, mode, components)
    # Run the node's loop
    try:
        node.loop()
    except KeyboardInterrupt:
        dbg("framework", "Interrupted by user, exiting")
    # except Exception:
    #     dbg("framework_error", "main loop caught: {}", ["death"])

    node.terminate()
    debugger.join()
    print_exit("Ya done now")


if __name__ == "__main__":
    main()
