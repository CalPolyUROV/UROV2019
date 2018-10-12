"""Configurable settings that apply to the operation of the robot
"""



# Sockets Connection
USE_SOCKETS = True
REQUIRE_SOCKETS = False
TOPSIDE_IP_ADDRESS = '192.168.0.101'
TOPSIDE_PORT = 5000
ROBOT_IPADDRESS = "192.168.10.10"
SOCKETS_MAX_ATTEMPTS = 5  # Maximum number of times to try creating or opening a socket


# Serial Connection
USE_SERIAL = True
REQUIRE_SERIAL = False
SERIAL_BAUD = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS: int = 4  # Maximum number of times to try openeing a serial port


# Debugging
PRINTING = True
LOGGING = False
