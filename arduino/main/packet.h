#ifndef PACKET_H
#define PACKET_H

//#include "TeensyThreads.h"

#include "defs.h"
#include "serial.h"

#define PACKET_LENGTH 3

// currently using switch statement and bodge LUT
#define EST_CON_CMD 0x10 // establish connection (call)
//#define EST_CON_ACK 0x11 // respond to new connection
#define SET_MOT_CMD 0x20 // set motor (call)
//#define SET_MOT_ACK 0x21 // motor has been set (reponse)

#define SET_CAM_CMD 0x33  // Set camera mux to a camera
#define RD_SENS_CMD 0x40 // TODO
#define BLINK_CMD   0x80 // blink
//#define BLINK_ACK   0x81 // blink has been activated (response)
#define INV_CMD_ACK 0xFF // Invalid command, value2 of response contains cmd


/* use for checking to see if buffer contains a packet.
  In the future, packet size could maybe grow to 8 bytes,
  allowing 4 packets to wait in the 64 byte UART buffer
*/

// Magic packet contents to validate est_con packet (arbitrary)
#define EST_CON_VAL1 0xa5
#define EST_CON_VAL2 0x5a

typedef struct packet {
  u8 cmd; // the action to be executed on the Arduino/Teensy
  u8 value1;
  u8 value2; // Data for the action ie which motor PWM timing
} packet;

// Take values for a packet and place at a pointer, add checksum
void create_packet(packet *p, u8 cmd, u8 value1, u8 value2) {
  p->cmd = cmd;
  p->value1 = value1;
  p->value2 = value2;
}



#endif
