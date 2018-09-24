import serial

SERIAL_BAUD = 9600
ENCODING = 'ascii'

CHKSUM_MASK = 0x0F

FIRST_SEQNUM = 0

EST_CON_CMD = 0x00
EST_CON_ACK = 0x01
SET_MOT_CMD = 0x20 # set motor (call)
SET_MOT_ACK = 0x21 # motor has been set (reponse)
RD_SENS_CMD = 0x40
INV_CMD_ACK = 0xFF # Invalid command, value2 of response contains cmd

EST_CON_VAL1 = 0b10100101
EST_CON_VAL2 = 0b01011010

class Packet:

    def calc_chksum(self, cmd, val1, val2, seqnum):
        return (cmd +
                (val1 * 3) +
                (val2 * 5) +
                (seqnum * 7)) & CHKSUM_MASK

    # Internal cosntructor
    def __init__(self, cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2
        self.seqnum_chksum = seqnum_chksum

    # Constructor for building packets to send (chksum is created)
    def make_packet(self, self, cmd: bytes, val1: bytes, val2: bytes, seqnum: bytes)
        return Packet(cmd, val1, val2, (seqnum << 4) + self.calc_chksum(cmd, value1, value2, seqnum))

    # Constructor for building packets that have been received, untrusted checksums
    def read_packet(self, cmd: bytes, value1: bytes, value2: bytes, seqnum_chksum: bytes) -> Packet
        if(calc_chksum(cmd, val1, val2, extract_seqnum(seqnum_chksum)) == extract_chksum(seqnum_chksum)):
            return Packet() 

    def __repr__(self):
        return """cmd: {}\n
        val1: {}\n
        val2: {}\n
        chksum_seqnum: {}""".format(self.cmd, self.value1, self.value2, self.seq)

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
    def get_packet(self) -> Packet:
        _cmd = self.serial_connection.read(size=1)
        _val1 = self.serial_connection.read(size=1)
        _val2 = self.serial_connection.read(size=1)
        _seqnum_chksum = self.serial_connection.read(size=1)
        return Packet(_cmd, _val1, _val2, _seqnum_chksum)
        # Warning, this will not catch packets with invalid checksums

    # Send the inital packet and wait for the correct response
    def establish_contact(self):
        self.send_packet(Packet(EST_CON_CMD, EST_CON_VAL1, EST_CON_VAL2, FIRST_SEQNUM))
        p = get_packet()
        if(p.cmd == EST_CON_ACK):
            # good
        else:
            # bad
