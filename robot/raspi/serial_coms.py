import serial

# Serial Baudrate, encoding scheme
SERIAL_BAUD = 9600
ENCODING = 'ascii'

# Bitmask for extracting checksums from seqnum_chksum
# Do not use directly, implement a checksum verification method
# TODO: verify checksums, probably in get_packet()
CHKSUM_MASK = 0x0F

# Initial value for sequence number
FIRST_SEQNUM = 0

# List of codes for each command
# we need to find a way to export this list and keep it synchronized
# TODO: Move list to external file (maybe .txt or .csv), 
#       write script to place in Arduino source and python source
#       will not be needed on topside Pi, only on robot
EST_CON_CMD = 0x00 # cmd of initial packet
EST_CON_ACK = 0x01 # cmd for response to initial packet
SET_MOT_CMD = 0x20 # set motor (call)
SET_MOT_ACK = 0x21 # motor has been set (reponse)
RD_SENS_CMD = 0x40 # request read sensor value
INV_CMD_ACK = 0xFF # Invalid command, value2 of response contains cmd

# Magic numbers to verify correct initial packet and response
EST_CON_VAL1 = 0b10100101
EST_CON_VAL2 = 0b01011010

class Packet:


    # Internal cosntructor
    def __init__(self, cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2
        self.seqnum_chksum = seqnum_chksum

    # Constructor for building packets to send (chksum is created)
    def make_packet(self, cmd: bytes, val1: bytes, val2: bytes, seqnum: bytes):
        return Packet(cmd, val1, val2, (seqnum << 4) + self.calc_chksum(cmd, val1, val2, seqnum))

    # Constructor for building packets that have been received, untrusted checksums
    def read_packet(self, cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        if(self.calc_chksum(cmd, val1, val2, self.extract_seqnum(seqnum_chksum)) == self.extract_chksum(seqnum_chksum)):
            return Packet(cmd, val1, val2, seqnum_chksum) 

    def extract_seqnum(self, seqnum_chksum: bytes) -> bytes:
        return seqnum_chksum >> 4

    def extract_chksum(self, seqnum_chksum: bytes) -> bytes:
        return seqnum_chksum & CHKSUM_MASK

    def calc_chksum(self, cmd, val1, val2, seqnum) -> bytes:
        return (cmd +
                (val1 * 3) +
                (val2 * 5) +
                (seqnum * 7)) & CHKSUM_MASK
        # idk, it has primes
        # TODO: Make this better, but it must match on this and the Arduino/Teensy. (Maybe CRC32?)

    def __repr__(self):
        return """cmd: {}\n
        val1: {}\n
        val2: {}\n
        chksum_seqnum: {}""".format(self.cmd, self.val1, self.val2, self.seqnum_chksum)

class SerialConnection:

    def __init__(self, serial_port):
        self.serial_connection = serial.Serial(
        port=serial_port,
        baudrate=9600,
        parity=serial.PARITY_NONE,   # parity is error checking, odd means the message will have an odd number of 1 bits
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
        timeout=0.1)

    # Send a Packet over serial
    def send_packet(self, p) -> None:
        # TODO: prevent the sending of invalid packets
        self.serial_connection.write(p.cmd)
        self.serial_connection.write(p.value1)
        self.serial_connection.write(p.value2)
        self.serial_connection.write(p.seqnum_chksum)

    # Read in a packet from serial
    def get_packet(self) -> Packet or None:
        _cmd = self.serial_connection.read(size=1)
        _val1 = self.serial_connection.read(size=1)
        _val2 = self.serial_connection.read(size=1)
        _seqnum_chksum = self.serial_connection.read(size=1)
        return Packet(_cmd, _val1, _val2, _seqnum_chksum)
        # Warning, this will not catch packets with invalid checksums

    # Send the inital packet and wait for the correct response
    def establish_contact(self):
        # Send initial packet
        self.send_packet(Packet(EST_CON_CMD, EST_CON_VAL1, EST_CON_VAL2, FIRST_SEQNUM))
        # Receive response
        p = self.get_packet()
        # TODO: Verify correctness of initial packet response from Arduino/Teensy
        #       Check arduino source to ensure order of response values, they might get flipped
        if(p.cmd == EST_CON_ACK): 
            # good
            return
        else:
            # bad 
            pass
