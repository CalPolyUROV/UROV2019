import serial

SERIAL_BAUD = 9600

class Packet:

    def calcChksum(cmd, value1, value2, seqnum):
        return (cmd +
                (value1 * 3) +
                (value2 * 5) +
                (seqnum_chksum * 7)) % B1111 & CHKSUM_MASK

    def __init__(self, cmd, value1, value2, seqnum):
        self.cmd = cmd
        self.value1 = value1
        self.value2 = value2
        self.seqnum_chksum = (seqnum << 4) +
                            calc_checksum(cmd, value1, value2, seqnum)

class SerialConnection:

    def __init__(self):
        self.outbound = serial.Serial(
        port=port,
        baudrate=9600,
        parity=serial.PARITY_NONE,   # parity is error checking, odd means the message should have an odd number of 1 bits
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
        timeout=0.1)

    def establish_contact():
        sendPacket(new Packet(0x00, 0x00, 0x00, 0x00))

    def send_packet(Packet p):
        # TODO: prevent the sending of invalid packets
        outbound.write(p.cmd)
        outbound.write(p.value1)
        outbound.write(p.value2)
        outbound.write(p.seqnum_chksum)
