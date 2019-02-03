"""Configurable settings that apply to the operation of the robot
"""
from enum import IntEnum

# TODO: Investigate converting settings values to a dict
# (Maybe keeping a per Node settings object)

# Debugging
# TODO: track debugging for server and client separately
DEBUGGING_DELAY_S = 0
DEBUG_PRINTING = True
DEBUG_LOGGING = False  # Not yet implemented
DEBUG_CHANNELS = {
    "framework": False,
    "schedule": False,
    "execute_task": False,

    "controller": False,
    "controls_reader": False,
    "controls_reader_verbose": False,
    "control_mappings": False,
    "control_mappings_verbose": False,
    "simulation": False,
    "simulation_verbose": False,

    "robot": True,
    "robot_control": True,
    "robot_control_verbose": False,
    "thrust_vec": True,
    "thrust_vec_verbose": False,

    "sockets": False,
    "sockets_client": True,
    "sockets_error": True,
    "sockets_warning": True,
    "sockets_event": True,
    "sockets_status": True,
    "sockets_verbose": False,

    "sockets_send": True,
    "sockets_send_verbose": False,

    "sockets_recieve": True,
    "sockets_receive_verbose": False,

    "encode": False,
    "encode_verbose": False,
    "decode": False,
    "decode_verbose": False,

    "serial_finder": True,
    "serial": True,
    "serial_con": True,
    "ser_packet": True,
    "chksum": True,

    "test": True,
}

# XBox Controller
USE_CONTROLLER = False  # TODO: Use this value
REQUIRE_CONTROLLER = True  # TODO: Use this value
SIMULATE_INPUT = False  # TODO: Use this value

# Mapping of pygame joystick output to values we can make sense of
# Examples:
# "pygame_name":["name_we_use"],
# "pygame_name":["name_we_use", scale_factor],
# "pygame_name":["name_we_use", scale_factor, shift_ammount],
# "pygame_name":["name_we_use", scale_factor, shift_ammount, dead_zone],
# to drop a value use "pygame_name":None,
control_mappings = {
    "number": [None],
    "name": [None],
    "axis_0": ["stick_left_x", 100],
    "axis_1": ["stick_left_y", 100],
    "axis_2": ["trigger_left", 100],
    "axis_3": ["stick_right_x", 100],
    "axis_4": ["stick_right_y", 100],
    "axis_5": ["trigger_right", 100],
    "button_0": ["button_a"],
    "button_1": ["button_b"],
    "button_2": ["button_x"],
    "button_3": ["button_y"],
    "button_4": ["button_left_bumper"],
    "button_5": ["button_right_bumper"],
    "button_6": ["button_back"],
    "button_7": ["button_start"],
    "button_8": ["button_xbox"],
    "button_9": ["button_left_stick"],
    "button_10": ["button_right_stick"],
    "dpad": ["dpad"],
    "num_buttons": [None],
    "num_dpad": [None],
    "num_axes": [None],
}


# Sockets Connection
USE_SOCKETS = False
REQUIRE_SOCKETS = True
TOPSIDE_IP_ADDRESS = '10.0.10.10'
TOPSIDE_PORT = 9120
SOCKETS_SERVER_TIMEOUT = 120
SOCKETS_CLIENT_TIMEOUT = 4
SOCKETS_OPEN_ATTEMPTS = 10  # Maximum number of times to try creating a socket
# Maximum number of times to try creating or opening a socket
SOCKETS_CONNECT_ATTEMPTS = 120
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 8192  # Maximum size for single receiving call
# note: SOCKETS_CONNECT_ATTEMPTS * SOCKETS_RETRY_WAIT = timeout for sockets connection
#     This timeout should be very long to allow the server to open its socket
#     before the client gives up on connecting to it.

# Serial Connection
USE_SERIAL = True
REQUIRE_SERIAL = False 
SERIAL_BAUD = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS = 4  # Maximum number of times to try openeing a serial port
SERIAL_RETRY_WAIT = 1  # Time to wait before retrying serial connection after failing

# Robot selection
ROBOT_NAME = "Subrina"
# ROBOT_NAME = "S5"

# -----Do NOT change anything below this line (To be modified at runtime only)-----

ROLE = "not set"  # Not a user facing setting
