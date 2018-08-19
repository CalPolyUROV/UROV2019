// packet.h

#include "defs.h"

#define PACKET_LENGTH 4 
// use for checking to see if buffer contains a packet

struct packet {
  byte cmd;
  byte value1, value2;
  byte seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};


void debug_packet(struct packet p) {
  if (DEBUG) {
    debug_serial->print("cmd: ");
    debug_serial->println(p.cmd);
    debug_serial->print("value1: ");
    debug_serial->println(p.value1);
    debug_serial->print("value2: ");
    debug_serial->println(p.value2);
    debug_serial->print("seq_num: ");
    debug_serial->println(extract_seqnum(p.seqnum_chksum));
    debug_serial->print("seq_num: ");
    debug_serial->println(extract_chksum(p.seqnum_chksum));
  }
}

// Mask off the first 4 bits of the seqnum_chksum byte to get the chksum nibble
byte extract_chksum(byte b) {
  return b & CHKSUM_MASK;
}

// Bitshift the seqnum_chksum byte right 4 times to leave just the seqnum nibble
byte extract_seqnum(byte b) {
  return b >> 4;
}

// calculate the checksum value for a packet
byte calc_chksum(struct packet* p) {
  return (p->cmd +
          (p->value1 * 3) +
          (p->value2 * 5) +
          (extract_seqnum(p->seqnum_chksum) * 7))
         & CHKSUM_MASK;
}
