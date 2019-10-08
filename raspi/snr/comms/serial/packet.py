"""Define sequences of packets to be sent over the serial connection
"""

import struct

PACKED_FORMAT = "BBB"


class Packet:
    """ Packet class representing information that is sent and received over
    the serial connection
    """

    def __init__(self, cmd: int, val1: int, val2: int):
        """Internal constructor
        """
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2

    def pack(self) -> (bytes, int):
        data_bytes = struct.pack(PACKED_FORMAT, self.cmd, self.val1, self.val2)
        expected_size = struct.calcsize(PACKED_FORMAT)
        return data_bytes, expected_size

    def weak_eq(self, other) -> bool:
        return ((self.__class__ == other.__class__) and
                (self.cmd == other.cmd) and
                (self.val1 == other.val1) and
                (self.val2 == other.val2))

    def __eq__(self, other) -> bool:
        return ((self.__class__ == other.__class__) and
                (self.cmd == other.cmd) and
                (self.val1 == other.val1) and
                (self.val2 == other.val2))

    def __repr__(self):
        s = "Packet: cmd: {} val1: {} val2: {}"
        return s.format(self.cmd,
                        self.val1,
                        self.val2)
