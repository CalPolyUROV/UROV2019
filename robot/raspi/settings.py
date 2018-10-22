"""Configurable settings that apply to the operation of the robot
"""

# Sockets Connection
USE_SOCKETS: bool = True
REQUIRE_SOCKETS: bool = False
TOPSIDE_IP_ADDRESS: str = 'localhost' #'192.168.0.101'
TOPSIDE_PORT: int = 5000


# Serial Connection
USE_SERIAL: bool = False
REQUIRE_SERIAL: bool = False
SERIAL_BAUD: int = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS: int = 2  # Maximum number of times to try openeing a serial port


# Debugging
PRINTING: bool = True
LOGGING: bool = False
