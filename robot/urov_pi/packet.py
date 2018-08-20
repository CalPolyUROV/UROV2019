
class packet:

    def __init__(self, cmd, value1, value2, seqnum):
        self.cmd = cmd
        self.value1 = value1
        self.value2 = value2
        self.seqnum_chksum = (seqnum << 4) + calc_checksum(cmd, value1, value2, seqnum)
        
def establishContact():
    sendPacket(new packet(0x00, 0x00, 0x00, 0x00))
   

def sendPacket(packet p):
    outbound.write(p.cmd)
    outbound.write(p.value1)
    outbound.write(p.value2)
    outbound.write(p.seqnum_chksum)
    
def calc_chksum(cmd, value1, value2, seqnum):
    return (cmd + (value1 * 3) + (value2 * 5) + (seqnum_chksum * 7)) % B1111 & CHKSUM_MASK