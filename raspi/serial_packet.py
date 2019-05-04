
from utils import debug


class Packet:
    """ Packet class representing information that is sent and received over
    the serial connection
    """

    def __init__(self, cmd: int, val1: int, val2: int, chksum: int):
        """Internal constructor
        """
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2
        self.chksum = chksum

    def isValid(self) -> bool:
        expected = calc_chksum(self.cmd, self.val1, self.val2)
        debug('chksum', "Packet had chksum of {}, {} was expected", [
            self.chksum, expected])
        return self.chksum == expected

    def weak_eq(self, other) -> bool:
        return ((self.__class__ == other.__class__) and
                (self.cmd == other.cmd) and
                (self.val1 == other.val1) and
                (self.val2 == other.val2))

    def __eq__(self, other) -> bool:
        return ((self.__class__ == other.__class__) and
                (self.cmd == other.cmd) and
                (self.val1 == other.val1) and
                (self.val2 == other.val2) and
                (self.chksum == other.chksum))

    def __repr__(self):
        s = "Packet: cmd: {} val1: {} val2: {} chksum: {}"
        return s.format(self.cmd,
                        self.val1,
                        self.val2,
                        self.chksum)


def calc_chksum(cmd: int, val1: int, val2: int) -> int:
    check_sum = (cmd +
                 (val1 * 3) +
                 (val2 * 5))
    return check_sum
    # idk, it has primes
    # TODO: Use CRC8 here and on the MCU


def parse_packet(cmd: bytes,
                 val1: bytes,
                 val2: bytes,
                 chksum: bytes) -> Packet:
    """Constructor for packets that have been received, untrusted checksums
    """
    debug("ser_packet",
          "Parsing packet: cmd: {}.{}, val1: {}.{}, val2: {}.{}",
          [cmd, cmd.__class__, val1, val1.__class__, val2, val2.__class__])
    cmd_int = int.from_bytes(cmd, byteorder='big')
    val1_int = int.from_bytes(val1, byteorder='big')
    val2_int = int.from_bytes(val2, byteorder='big')
    chksum_int = int.from_bytes(chksum, byteorder='big')
    p = Packet(cmd_int, val1_int, val2_int, chksum_int)
    return p
