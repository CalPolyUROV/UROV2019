"""Configurable settings that apply to the operation of the robot
"""

ROLE = "not set"  # Not a user facing setting

# Debug channels
CHANNELS = {"schedule": True,
            "execute_task": True,
            "sockets": True,
            "socket_con": True,
            "encode": False,
            "decode": False,
            "serial_finder": True,
            "serial": True,
            "serial_con":True,
            "packet":True}


# Sockets Connection
USE_SOCKETS = True
REQUIRE_SOCKETS = True
TOPSIDE_IP_ADDRESS = "localhost" # '192.168.137.127'
TOPSIDE_PORT = 9120
ROBOT_IPADDRESS =  "localhost" # "192.168.137.50"
SOCKETS_MAX_ATTEMPTS = 2  # Maximum number of times to try creating or opening a socket
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 1024  # Maximum size for single receiving call


# Serial Connection
USE_SERIAL = True
REQUIRE_SERIAL = True
SERIAL_BAUD = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS = 2  # Maximum number of times to try openeing a serial port


# Debugging
# TODO: track debugging for server and client separately
PRINTING = True
LOGGING = False
