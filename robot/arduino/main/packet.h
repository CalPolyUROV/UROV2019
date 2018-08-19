#ifndef PACKET_H
#define PACKET_H

#include "defs.h"

#define PACKET_LENGTH 4 
// use for checking to see if buffer contains a packet

struct packet {
  byte cmd;
  byte value1, value2;
  byte seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};

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

#endif
