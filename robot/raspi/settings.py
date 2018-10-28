"""Configurable settings that apply to the operation of the robot
"""

ROLE = "not set"  # Not a user facing setting

# Debug channels
CHANNELS = {"schedule": True,
            "execute_task": True,
            "sockets": False,
            "socket_con": False,
            "encode": True,
            "decode": True,
            "serial_finder": True,
            "serial": True,
            "serial_con":True,
            "packet":True}


# Sockets Connection
USE_SOCKETS = False
REQUIRE_SOCKETS = False
TOPSIDE_IP_ADDRESS = "localhost" # '192.168.137.127'
TOPSIDE_PORT = 9120
ROBOT_IPADDRESS =  "localhost" # "192.168.137.50"
SOCKETS_MAX_ATTEMPTS = 2  # Maximum number of times to try creating or opening a socket
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 1024  # Maximum size for single receiving call


# Serial Connection
USE_SERIAL = True
REQUIRE_SERIAL = True
SERIAL_MAX_ATTEMPTS = 2  # Maximum number of times to try openeing a serial port
SERIAL_BAUD = 19200  # Serial Baudrate


# Debugging
# TODO: track debugging for server and client separately
PRINTING = True
LOGGING = False
