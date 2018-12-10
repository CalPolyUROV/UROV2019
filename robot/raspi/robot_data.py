import robot_data

class Database:

    def __init__(self):
        self.control_input = {}
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
