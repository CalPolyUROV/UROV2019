#ifndef PACKET_H
#define PACKET_H

#include <arduino.h>

#include "defs.h"

//LUT
// lookup table for indexes of commands
// byte cmd_lut[255] = {EST_CMD, SET_MOT_CMD, READ...}
// currently using switch statement and bodge LUT
#define EST_CON_CMD 0x00 // establish connection (call) // TODO: EST packet should be different from empty packet
#define EST_CON_ACK 0x01 // respond to new connection
#define SET_MOT_CMD 0x20 // set motor (call)
#define SET_MOT_ACK 0x21 // motor has been set (reponse)
#define RD_SENS_CMD 0x40
#define INV_CMD_ACK 0xFF // Invalid command, value2 of response contains cmd


#define PACKET_LENGTH 4
/* use for checking to see if buffer contains a packet.
  In the future, packet size could maybe grow to 8 bytes,
  allowing 4 packets to wait in the 64 byte UART buffer
*/

// Magic packet contents to validate est_con packet (arbitrary)
#define EST_CON_VAL1 B10100101
#define EST_CON_VAL2 B01011010

#define CHKSUM_MASK LOWER_NIBBLE_MASK

#define MAX_SEQNUM B00001111  //upper bound of seqnum, inclusive
#define FIRST_SEQNUM B00000000 // initial sequence number

struct packet {
  byte cmd; // the action to be executed on the Arduino/Teensy
  byte value1, value2; // Data for the action ie which motor PWM timing
  byte seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};

void wait_for_packet(SERIAL_CLASS *serial);
void create_packet(struct packet *p, byte cmd, byte value1, byte value2, byte seqnum_nibble);
void send_packet(SERIAL_CLASS *serial, packet p);
byte calc_chksum(byte cmd, byte value1, byte value2, byte seqnum_nibble);
byte extract_chksum(byte seqnum_chksum);
byte extract_seqnum(byte b);

#endif
