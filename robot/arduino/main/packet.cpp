#include "packet.h"

void create_packet(struct packet *p, byte cmd, byte value1, byte value2, byte seqnum_nibble) {
  p->cmd = cmd;
  p->value1 = value1;
  p->value2 = value2;
  p->seqnum_chksum = (seqnum_nibble << 4) +  calc_chksum(cmd, value1, value2, seqnum_nibble);
}

// Mask off the first 4 bits of the seqnum_chksum byte to get the chksum nibble
byte extract_chksum(byte seqnum_chksum) {
  return seqnum_chksum & CHKSUM_MASK;
}

// Bitshift the seqnum_chksum byte right 4 times to leave just the seqnum nibble
byte extract_seqnum(byte b) {
  return b >> 4;
}

// calculate the checksum for values being put into a packet
byte calc_chksum(byte cmd, byte value1, byte value2, byte seqnum_nibble) {
  return ((cmd +
           (value1 * 3) +
           (value2 * 5) +
           (seqnum_nibble * 7))
          % B1111)
         & CHKSUM_MASK;
}

byte recalc_chksum(struct packet *p) {
  return calc_chksum(p->cmd, p->value1, p->value2, p->seqnum_chksum >> 4);
}