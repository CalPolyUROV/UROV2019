"""Configurable settings that apply to the operation of the robot
"""

ROLE = "not set"  # Not a user facing setting

# Debug channels
CHANNELS = {"schedule": True,
            "execute_task": True,
            "sockets": False,
            "socket_con": False,
            "encode": False,
            "decode": True,
            "serial_finder": True,
            "serial": True,
            "serial_con":True}


# Sockets Connection
USE_SOCKETS: bool = True
REQUIRE_SOCKETS: bool = False
TOPSIDE_IP_ADDRESS: str = 'localhost' #'192.168.0.101'
TOPSIDE_PORT: int = 5000
ROBOT_IPADDRESS: str = 'localhost' #"192.168.10.10"
SOCKETS_MAX_ATTEMPTS: int = 2  # Maximum number of times to try creating or opening a socket
SOCKETS_RETRY_WAIT:int = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE: int = 1024  # Maximum size for single receiving call


# Serial Connection
USE_SERIAL: bool = False
REQUIRE_SERIAL: bool = False
SERIAL_BAUD: int = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS: int = 2  # Maximum number of times to try openeing a serial port


# Debugging
# TODO: track debugging for server and client separately
PRINTING: bool = True
LOGGING: bool = False
