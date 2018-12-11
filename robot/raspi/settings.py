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
    "simulation": True,
    "robot_control": True,

    "sockets": True,
    "socket_con": False,
    "encode": False,
    "decode": False,

    "serial_finder": False,
    "serial": False,
    "serial_con": True,
    "ser_packet": True,
    "chksum": False,

    "test": True,
}

# XBox Controller
USE_CONTROLLER = True  # TODO: Use this value
REQUIRE_CONTROLLER = False  # TODO: Use this value
SIMULATE_INPUT = True  # TODO: Use this value

# Mapping of pygame joystick output to values we can make sense of
# "pygame_name":"name_we_use",
# to drop a value use "pygame_name":None,
control_mappings = {
    "number": None,
    "name": None,
    "axis_0": "axis_0",
    "axis_1": "axis_1",
    "axis_2": "axis_2",
    "axis_3": "axis_3",
    "axis_4": "axis_4",
    "axis_5": "axis_5",
    "button_0": "button_a",
    "button_1": "button_b",
    "button_2": "button_x",
    "button_3": "button_y",
    "button_4": "button_4",
    "button_5": "button_5",
    "button_6": "button_6",
    "button_7": "button_7",
    "button_8": "button_8",
    "button_9": "button_9",
    "button_10": "button_10",
    "dpad": "dpad",
    "num_buttons": None,
    "num_dpad": None,
    "num_axes": None,
}


# Sockets Connection
USE_SOCKETS = True
REQUIRE_SOCKETS = False
TOPSIDE_IP_ADDRESS = "localhost"  # '192.168.137.127'
TOPSIDE_PORT = 9120
ROBOT_IPADDRESS = "localhost"  # "192.168.137.50"
SOCKETS_MAX_ATTEMPTS = 2  # Maximum number of times to try creating or opening a socket
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 1024  # Maximum size for single receiving call


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
