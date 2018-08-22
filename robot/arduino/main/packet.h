#ifndef PACKET_H
#define PACKET_H

#include <arduino.h>

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


void create_packet(struct packet *p, byte cmd, byte value1, byte value2, byte seqnum_nibble);
byte calc_chksum(byte cmd, byte value1, byte value2, byte seqnum_nibble);
byte extract_chksum(byte seqnum_chksum);
byte extract_seqnum(byte b);

#endif
