
from utils import debug

# Bitmask for extracting checksums from seqnum_chksum
# Do not use directly, implement a checksum verification method
# TODO: verify checksums, probably in read_packet()
CHKSUM_MASK = 0b00001111


class Packet:
    """ Packet class for storing information that is sent and received over serial
    """

    def __init__(self, cmd: int, val1: int, val2: int, seqnum_chksum: int):
        """Internal constructor
        """
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2
        self.seqnum_chksum = seqnum_chksum

        # debug("ser_packet", "Constructed: {}", [self])

    def extract_seqnum(self, seqnum_chksum: int) -> int:
        return int.from_bytes(seqnum_chksum, byteorder='big') >> 4

    def get_seqnum(self) -> int:
        return self.seqnum_chksum >> 4

    def extract_chksum(self, seqnum_chksum: int) -> int:
        return seqnum_chksum & CHKSUM_MASK

    def get_chksum(self) -> int:
        return self.seqnum_chksum & CHKSUM_MASK

    def isValid(self) -> bool:
        chksum = self.get_chksum()
        expected = Packet.calc_chksum(self.cmd, self.val1, self.val2, self.get_seqnum())
        debug('chksum', "Packet had chksum of {}, {} was expected", [
                chksum, expected])
        return chksum == expected

    def __eq__(self, other) -> bool:
        return ((self.__class__ == other.__class__) and
                (self.cmd == other.cmd) and
                (self.val1 == other.val1) and
                (self.val2 == other.val2) and
                (self.seqnum_chksum == other.seqnum_chksum))

    def __repr__(self):
        return "Packet: cmd: {} val1: {} val2: {} seqnum: {} chksum: {}".format(self.cmd, self.val1, self.val2, self.get_seqnum(), self.get_chksum())

    def parse_packet(cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        """Constructor for building packets that have been received, untrusted checksums
        """
        _cmd = int.from_bytes(cmd, byteorder='big')
        _val1 = int.from_bytes(val1, byteorder='big')
        _val2 = int.from_bytes(val2, byteorder='big')
        _seqnum = int.from_bytes(seqnum_chksum, byteorder='big') >> 4
        _chksum = int.from_bytes(seqnum_chksum, byteorder='big') & CHKSUM_MASK
        p = Packet(_cmd, _val1, _val2, ((_seqnum << 4) + _chksum))
        if(p.isValid()):
            return p
        else:
            debug("ser_packet", "read invalid packet {}", [p])

    def calc_chksum(cmd: int, val1: int, val2: int, seqnum: int) -> int:
        sum = (cmd +
               (val1 * 3) +
               (val2 * 5) +
               (seqnum * 7)) & CHKSUM_MASK
        return sum
        # idk, it has primes
        # TODO: Make this better, but it must match on this and the Arduino/Teensy. (Maybe CRC32 or a smaller variant)

