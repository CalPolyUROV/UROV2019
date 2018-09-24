import serial

SERIAL_BAUD = 9600
CHKSUM_MASK = 0x0F

class Packet:

    def calc_chksum(self, cmd, value1, value2, seqnum):
        return (cmd +
                (value1 * 3) +
                (value2 * 5) +
                (seqnum * 7)) & CHKSUM_MASK

    def __init__(self, cmd, value1, value2, seqnum):
        self.cmd = cmd
        self.value1 = value1
        self.value2 = value2
        self.seqnum_chksum = (seqnum << 4) + calc_chksum(cmd, value1, value2, seqnum)

class SerialConnection:

    def __init__(self, serial_port):
        self.serial_connection = serial.Serial(
        port=serial_port,
        baudrate=9600,
        parity=serial.PARITY_NONE,   # parity is error checking, odd means the message will have an odd number of 1 bits
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
        timeout=0.1)

    def send_packet(self, p):
        # TODO: prevent the sending of invalid packets
        self.serial_connection.write(p.cmd)
        self.serial_connection.write(p.value1)
        self.serial_connection.write(p.value2)
        self.serial_connection.write(p.seqnum_chksum)

    def establish_contact(self):
        send_packet(Packet(0x00, 0x00, 0x00, 0x00))
