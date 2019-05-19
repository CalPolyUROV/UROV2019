"""Configurable settings that apply to the operation of the robot

Note: settings exists per imported "namespace" such that each file
that imports settings has its own copy and changes do not propagate to
other copies. In other words, if a setting here is changed from inside
a specific file, it will not be updated for other files.
"""

from snr_sockets import SocketsConfig

# TODO: Investigate converting settings values to an object
# (Maybe keeping a per Node settings object)

# Debugging printing and logging
# TODO: Track debugging for server and client separately
DEBUGGING_DELAY_S = 0
DEBUG_PRINTING = True
DEBUG_LOGGING = False  # Not yet implemented
DEBUG_CHANNELS = {
    "framework": True,
    "schedule": True,
    "schedule_verbose": False,
    "execute_task": True,
    "execute_task_verbose": False,

    "clui": True,

    "datastore": True,
    "datastore_error": True,
    "datastore_event": False,
    "datastore_verbose": False,

    "controller": True,
    "controller_error": True,
    "controller_event": False,
    "controller_verbose": False,
    "controls_reader": True,
    "controls_reader_verbose": False,
    "control_mappings": False,
    "control_mappings_verbose": False,
    "simulation": True,
    "simulation_verbose": False,

    "robot": True,
    "robot_verbose": False,

    "robot_control": True,
    "robot_control_warning": True,
    "robot_control_event": False,
    "robot_control_verbose": False,

    "thrust_vec": True,
    "thrust_vec_verbose": False,

    "throttle": True,
    "throttle_values": True,
    "throttle_verbose": False,
    "axis_update_verbose": False,

    "sockets": True,
    "sockets_client": True,
    "sockets_server": True,
    "sockets_error": True,
    "sockets_warning": True,
    "sockets_event": False,
    "sockets_status": False,
    "sockets_verbose": False,

    "sockets_send": True,
    "sockets_send_verbose": False,

    "sockets_receive": False,
    "sockets_receive_verbose": False,

    "encode": False,
    "encode_verbose": False,
    "decode": False,
    "decode_verbose": False,

    "int_temp_mon": True,

    "serial_finder": True,
    "serial": True,
    "serial_error": True,
    "serial_warning": True,
    "serial_verbose": False,

    "serial_packet": True,
    "chksum_error": True,
    "chksum_verbose": False,

    "sleep": True,
    "try_key": False,

    "test": True,
}
THREAD_END_WAIT_S = 2
DISABLE_SLEEP = False


# Command Line User Interface
USE_TOPSIDE_CLUI = False
TOPSIDE_CLUI_NAME = "topside_clui"
UI_DATA_KEY = "UI_data"
TOPSIDE_UI_TICK_RATE = 24  # Hz (Times per second)

# XBox Controller
USE_CONTROLLER = True
REQUIRE_CONTROLLER = False
SIMULATE_INPUT = True
CONTROLLER_NAME = "topside_xbox_controller"
CONTROLLER_INIT_TICK_RATE = 1
CONTROLLER_TICK_RATE = 30  # Hz (Times per second)
CONTROLLER_ZERO_TRIGGERS = True
'''Mapping of pygame joystick output to values we can make sense of
Examples:
"pygame_name": ["name_we_use"],
"pygame_name": ["name_we_use", cast_type],
"pygame_name": ["name_we_use", cast_type, scale_factor],
"pygame_name": ["name_we_use", cast_type, scale_factor, shift_ammount],
"pygame_name": ["name_we_use", cast_type, scale_factor, shift_ammount,
                 dead_zone],
to drop a value use "pygame_name": [None],
'''
control_mappings = {
    "number": [None],
    "name": ["controller_name"],
    "axis_0": ["stick_left_x", int,  100],
    "axis_1": ["stick_left_y", int, -100],
    "axis_2": ["trigger_left", int, 50, 50],
    "axis_3": ["stick_right_x", int, 100],
    "axis_4": ["stick_right_y", int, -100],
    "axis_5": ["trigger_right", int, 50, 50],
    "button_0": ["button_a", bool],
    "button_1": ["button_b", bool],
    "button_2": ["button_x", bool],
    "button_3": ["button_y", bool],
    "button_4": ["button_left_bumper", bool],
    "button_5": ["button_right_bumper", bool],
    "button_6": ["button_back", bool],
    "button_7": ["button_start", bool],
    "button_8": ["button_xbox", bool],
    "button_9": ["button_left_stick", bool],
    "button_10": ["button_right_stick", bool],
    "dpad": ["dpad", tuple],
    "num_buttons": [None],
    "num_dpad": [None],
    "num_axes": [None],
}

# Robot Control
THROTTLE_DATA_NAME = "robot_throttle_data"

# Motor control
MOTOR_CONTROL_NAME = "motor_control_data"
MOTOR_CONTROL_TICK_RATE = 20
DEFAULT_MOTOR_VALUE = 0
NUM_MOTORS = 6
MOTOR_MAX_DELTA = 10

# Cameras
NUM_ANALOG_CAMERAS = 2

# Sockets Connection
TOPSIDE_IP = "10.0.10.10"
ROBOT_IP = "10.0.10.11"
SOCKETS_SERVER_TIMEOUT = 640
SOCKETS_CLIENT_TIMEOUT = 4
SOCKETS_OPEN_ATTEMPTS = 10  # Maximum number of times to try creating a socket
SOCKETS_MAX_CONNECTIONS = 2  # Maximun concurrent connections
# Should only ever be 1, after 2 thigns have gone very wrong
# Maximum number of times to try creating or opening a socket
SOCKETS_CONNECT_ATTEMPTS = 120
SOCKETS_RETRY_WAIT = 1  # seconds to wait before retrying sockets connection
MAX_SOCKET_SIZE = 8192  # Maximum size for single receiving call
'''Note: SOCKETS_CONNECT_ATTEMPTS * SOCKETS_RETRY_WAIT = timeout for sockets
    connection
    This timeout should be very long to allow the server to open its socket
    before the client gives up on connecting to it.
'''

# Controls Sockets Connection
USE_CONTROLS_SOCKETS = True
REQUIRE_CONTROLS_SOCKETS = True
controls_server_ip = TOPSIDE_IP
controls_server_port = 9120
CONTROLS_SOCKETS_CONFIG = SocketsConfig(controls_server_ip,
                                        controls_server_port,
                                        REQUIRE_CONTROLS_SOCKETS)

# Telemetry Sockets Connection
USE_TELEMETRY_SOCKETS = False
REQUIRE_TELEMETRY_SOCKETS = False
telemetry_server_ip = ROBOT_IP
telemetry_server_port = 9121
TELEMETRY_SOCKETS_CONFIG = SocketsConfig(telemetry_server_ip,
                                         telemetry_server_port,
                                         REQUIRE_TELEMETRY_SOCKETS)
TELEMETRY_DATA_NAME = "telemetry_data"


# Serial Connection
USE_SERIAL = False
REQUIRE_SERIAL = False
SERIAL_BAUD = 9600  # Serial Baudrate
SERIAL_MAX_ATTEMPTS = 4  # Maximum number of times to try openeing serial port
SERIAL_RETRY_WAIT = 0.5  # Time to wait before retrying serial connection
SERIAL_TIMEOUT = 4
SERIAL_SETUP_WAIT_PRE = 1
SERIAL_SETUP_WAIT_POST = 1

# Temperature Monitor
USE_TOPSIDE_PI_TEMP_MON = False
USE_ROBOT_PI_TEMP_MON = False
TOPSIDE_INT_TEMP_NAME = "topside_int_temp_mon"
ROBOT_INT_TEMP_NAME = "robot_int_temp_mon"
INT_TEMP_MON_TICK_RATE = 0.25  # Hz (Readings per second)
INT_TEMP_MON_AVG_PERIOD = 4  # Number of readings to average over

# Robot selection
ROBOT_NAME = "S5"
