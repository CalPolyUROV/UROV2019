from typing import List

import settings
from robot_controls import RobotControlsFactory
from snr.camera.factory import CameraManagerPair
from snr.comms.serial.factory import SerialFactory
from snr.comms.sockets.factory import EthernetLink
from snr.dds.sockets.sockets_dds import SocketsDDSFactory
from snr.io.controller.factory import ControllerFactory
from snr.utils.utils import get_all
from snr.zynq.factory import ZyboFactory
from ui.gui.factory import GUIFactory


def enumerate_components():
    # Connections between devices
    # Ethernet tether link for control data
    # controls_link = EthernetLink(settings.CONTROLS_SOCKETS_CONFIG.port,
    #                              settings.CONTROLS_DATA_NAME)
    # # Ethernet tether link for telemetry data
    # telemetry_link = EthernetLink(settings.TELEMETRY_SOCKETS_CONFIG.port,
    #                               settings.TELEMETRY_DATA_NAME)
    # DDS Sockets Connection test
    sockets_link = EthernetLink(settings.SOCKETS_HOSTS,
                                settings.SOCKETS_PORT)

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
        "main_camera0": 0,
        "ir_camera1": 1,
        "ir_camera2": 2,
        "ir_camera3": 3,
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

    roles = {
        "topside": [
            # controls_link.server,
            #   telemetry_link.client,
            sockets_link,
            controller,
            #   GUI,
            cameras.receiver
        ],
        "robot": [
            # controls_link.client,
            # telemetry_link.server,
            robot_controls,
            serial_link,
            cameras.source
        ],
        "zybo": [
            # controls_link.client,
            # telemetry_link.server,
            robot_controls,
            zynq_link
        ]
    }
    return roles


def get_components(role: str, mode: str) -> List:
    component_libraries = enumerate_components()
    components = component_libraries.get(role)
    return components
