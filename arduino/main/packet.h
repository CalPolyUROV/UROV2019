#ifndef PACKET_H
#define PACKET_H

//#include "TeensyThreads.h"

#include "defs.h"
#include "serial.h"

//LUT
// lookup table for indexes of commands
// u8 cmd_lut[255] = {EST_CMD, SET_MOT_CMD, READ...}
// currently using switch statement and bodge LUT
#define EST_CON_CMD 0x10 // establish connection (call)
#define EST_CON_ACK 0x11 // respond to new connection
#define SET_MOT_CMD 0x20 // set motor (call)
#define SET_MOT_ACK 0x21 // motor has been set (reponse)
#define RD_SENS_CMD 0x40 // TODO
#define BLINK_CMD   0x80 // blink
#define BLINK_ACK   0x81 // blink has been activated (response)
#define INV_CMD_ACK 0xFF // Invalid command, value2 of response contains cmd


#define PACKET_LENGTH 4
/* use for checking to see if buffer contains a packet.
  In the future, packet size could maybe grow to 8 bytes,
  allowing 4 packets to wait in the 64 byte UART buffer
*/

// Magic packet contents to validate est_con packet (arbitrary)
#define EST_CON_VAL1 0xa5
#define EST_CON_VAL2 0x5a

#define LOWER_NIBBLE_MASK 0x0f
#define UPPER_NIBBLE_MASK 0xf0
#define CHKSUM_MASK LOWER_NIBBLE_MASK

struct packet {
  u8 cmd; // the action to be executed on the Arduino/Teensy
  u8 value1, value2; // Data for the action ie which motor PWM timing
  u8 seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};
//
//// Getter for global sequence number
//u8 get_seqnum_nibble() {
//  return seqnum & LOWER_NIBBLE_MASK;
//}

// Mask off the first 4 bits of the seqnum_chksum byte to get the chksum nibble
//u8 extract_chksum(u8 seqnum_chksum) {
//  return seqnum_chksum & CHKSUM_MASK;
//}

// Bitshift the seqnum_chksum byte right 4 times to leave just the seqnum nibble
//u8 extract_seqnum(u8 b) {
//  return b >> 4; // is this wrong?
//}

// calculate the checksum for values being put into a packet
u8 calc_chksum(u8 cmd, u8 value1, u8 value2, u8 seqnum_nibble) {
  return (cmd +
          (value1 * 3) +
          (value2 * 5) +
          (seqnum_nibble * 7))
         & CHKSUM_MASK;
}



// Take values for a packet and place at a pointer, add checksum
void create_packet(packet *p, u8 cmd, u8 value1, u8 value2, u8 seqnum_nibble) {
  p->cmd = cmd;
  p->value1 = value1;
  p->value2 = value2;
  p->seqnum_chksum = '0'; //(seqnum_nibble << 4) +  calc_chksum(cmd, value1, value2, seqnum_nibble);
}



/* not used right now

  u8 recalc_chksum(struct packet *p) {
  return calc_chksum(p->cmd, p->value1, p->value2, p->seqnum_chksum >> 4);
  }
*/

#endif
