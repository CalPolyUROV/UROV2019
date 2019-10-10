"""Define sequences of packets to be sent over the serial connection
"""

import struct


# encoding scheme
ENCODING = 'ascii'
PACKET_SIZE = 3

PACKED_FORMAT = "".join(["B" for x in range(PACKET_SIZE)])


""" List of codes for each command """
# TODO: Move command list to external file (maybe .txt or .csv),
#       write script to generate in Arduino source and python
#       source will not be needed on topside Pi, only on robot
SET_MOT_CMD = 0x20      # set motor speed
SET_CAM_CMD = 0x33      # set camera feed
RD_SENS_CMD = 0x40      # request read sensor value
BLINK_CMD = 0x80
INV_CMD_ACK = 0xFF      # Invalid command, value2 of response contains cmd


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
