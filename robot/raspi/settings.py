"""Configurable settings that apply to the operation of the robot
"""

# TODO: Investigate converting settings values to a dict
# (Maybe keeping a per Node settings struct)

# Debug channels
DEBUG_CHANNELS = {
    "framework": True,
    "schedule": False,
    "execute_task": False,
    "controller": True,
    "simulation": False,
    "simulation_verbose":False,
    "robot_control": True,
    "robot_control_verbose": False,
    "thrust_vec": True,
    "thrust_vec_verbose":True,

    "sockets": True,
    "sockets_server": True,
    "sockets_client": True,
    "socket_con": True,
    "socket_con_verbose":False,
    "encode": False,
    "decode": False,
    "decode_verbose": False,

    "serial_finder": False,
    "serial": False,
    "serial_con": True,
    "ser_packet": True,
    "chksum": False,

    "test": True,
}

# XBox Controller
USE_CONTROLLER = True  # TODO: Use this value
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
USE_SOCKETS = True
REQUIRE_SOCKETS = True
TOPSIDE_IP_ADDRESS = "localhost"  # '192.168.10.10'
TOPSIDE_PORT = 9120
# ROBOT_IPADDRESS = '192.168.10.11'  # "192.168.137.50"  # Not used
SOCKETS_OPEN_ATTEMPTS = 4  # Maximum number of times to try creating a socket
SOCKETS_CONNECT_ATTEMPTS = 120  # Maximum number of times to try creating or opening a socket
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 2048  # Maximum size for single receiving call
# note: SOCKETS_CONNECT_ATTEMPTS * SOCKETS_RETRY_WAIT = timeout for sockets connection
#     This timeout should be very long to allow the server to open its socket
#     before the client gives up on connecting to it.

# Serial Connection
USE_SERIAL = False
REQUIRE_SERIAL = True
SERIAL_BAUD = 19200  # Serial Baudrate
SERIAL_MAX_ATTEMPTS = 4  # Maximum number of times to try openeing a serial port

# Debugging
# TODO: track debugging for server and client separately
PRINTING = True
LOGGING = False

# Robot selection
ROBOT_NAME = "Subrina"
# ROBOT_NAME = "S5"

# -----Do NOT change anything below this line while trying to Configurable-----

ROLE = "not set"  # Not a user facing setting
