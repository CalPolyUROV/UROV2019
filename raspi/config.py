
from typing import Dict, List

from main import MODE_DEBUG, MODE_DEPLOYED
from robot_controls import RobotControlsFactory
from snr.camera.factory import CameraManagerPair
from snr.comms.serial.factory import SerialFactory
from snr.comms.sockets.factory import EthernetLink
from snr.dds.sockets.sockets_dds import SocketsDDSFactory
from snr.factory import Factory
from snr.io.controller.factory import ControllerFactory
from snr.utils.recorder import RecorderFactory
from snr.utils.utils import get_all
from snr.zynq.factory import ZyboFactory
from ui.gui.factory import GUIFactory

DEBUG_IP = "localhost"
TOPSIDE_IP = "10.0.10.10"
ROBOT_IP = "10.0.10.11"

CONTROLS_DATA_NAME = "controls_data"
MOTOR_CONTROL_NAME = "motor_control_data"
MOTOR_DATA_NAME = "motor_data"

SENSOR_DATA_NAME = "sensor_data"
TELEMETRY_DATA_NAME = "telemetry_data"


def __enumerate_components(mode: str):
    # DDS Sockets Connection test
    sockets_dds = SocketsDDSFactory(
        hosts={
            MODE_DEBUG: [DEBUG_IP, DEBUG_IP],
            MODE_DEPLOYED: [TOPSIDE_IP, ROBOT_IP]
        }.get(mode),
        port=9120)

    # XBox Controller
    controller = ControllerFactory(CONTROLS_DATA_NAME)

    # GUI
    user_interface = GUIFactory([CONTROLS_DATA_NAME,
                                 TELEMETRY_DATA_NAME])

    # Controls and motor processing
    robot_controls = RobotControlsFactory(CONTROLS_DATA_NAME,
                                          MOTOR_DATA_NAME)

    # UART/USB link to Arduino for motor control and sensor reading
    serial_link = SerialFactory(MOTOR_DATA_NAME, SENSOR_DATA_NAME,
                                "path_to_arduino_program(unimplemented)")

    # Zynq Zybo Z7-20: replaces serial link for specific role
    zynq_link = ZyboFactory(MOTOR_DATA_NAME, SENSOR_DATA_NAME)

    # Cameras
    cameras = CameraManagerPair(
        {
            MODE_DEBUG: {
                "main_camera0": 0, },
            MODE_DEPLOYED: {
                "main_camera0": 0,
                "ir_camera1": 1,
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
            }
        }.get(mode))

    event_recorder = RecorderFactory("Controls Recorder", [CONTROLS_DATA_NAME])

    # Assign components to roles
    return {
        "topside": [
            sockets_dds,
            # controls_link.server,
            #   telemetry_link.client,
            controller,
            user_interface,
            # cameras.receiver,
            event_recorder
        ],
        "robot": [
            sockets_dds,
            # controls_link.client,
            # telemetry_link.server,
            robot_controls,
            serial_link,
            # cameras.source
            event_recorder
        ],
        "zybo": [
            sockets_dds,
            # controls_link.client,
            # telemetry_link.server,
            robot_controls,
            zynq_link
        ]
    }


def get(mode: str) -> Dict[str, List[Factory]]:
    return __enumerate_components(mode)
