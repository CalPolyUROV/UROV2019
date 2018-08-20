#ifndef PACKET_H
#define PACKET_H

#include "defs.h"

//LUT
// lookup table for indexes of commands
// byte cmd_lut[255] = {EST_CMD, SET_MOT_CMD, READ...}
// currently using switch statement and bodge LUT
#define EST_CON_CMD 0x00 // establish connection (command)
#define SET_MOT_CMD 0x20 // set motor (command)
#define MOT_SET_CMD 0x21 // motor has been set (reponse)
#define RD_SENS_CMD 0x40


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

// calculate the checksum for values being put into a packet
byte calc_chksum(byte cmd, byte value1, byte value2, byte seqnum) {
  return ((cmd +
           (value1 * 3) +
           (value2 * 5) +
           (seqnum * 7))
          % B1111)
          & CHKSUM_MASK;
}

byte recalc_chksum(struct packet *p){
  return calc_chksum(p->cmd, p->value1, p->value2, p->seqnum_chksum >> 4);
}

#endif
