import robot_data

class Database:
    """Stores data for the robot
    Data includes sensor values and control inputs
    Implemented sensors:
        -None
    Senors TODO:
        -Acceleration and Orientation
        -Temperature (required by MATE comp)
        -pH (required by MATE comp)
        -Camera (if visible to python)
    Implemented inputs:
        -None
    Inputs TODO:
        -Motor speeds
        -Mission tools
        -Camera switching
    """

    def __init__(self):
        """Create data structures to hold implented data
        """
        self.control_input = {}
        self.previous_cntl_input = {}
        self.motor_speeds = [range(6)]
        self.acceleration = robot_data.Acceleration(0, 0, 0)
        self.orientation = robot_data.Orientation(0, 0, 0)

    def telemetry_data(self) -> list:
        return [self.acceleration, self.orientation]

class Acceleration:
    def __init__(self, _x: int, _y: int, _z: int):
        self.x = _x
        self.y = _y
        self.z = _z

    def __repr__(self):
        return self.x.__repr__() + ", " + self.y.__repr__() + ", " + self.z.__repr__()

class Orientation:
    def __init__(self, _roll: int, _pitch: int, _yaw: int):
        self.roll = _roll
        self.pitch = _pitch
        self.yaw = _yaw

    def __repr__(self):
        return self.roll.__repr__() + ", " + self.pitch.__repr__() + ", " + self.yaw.__repr__()
