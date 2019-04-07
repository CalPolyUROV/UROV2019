#ifndef SERIAL_H
#define SERIAL_H

#include "defs.h"
#include "settings.h"
#include "packet.h"
#include "blink.h"

void initialize_serial() {
  Serial.begin(COMS_BAUD);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
}

// Wait for the UART buffer to be filled with a whole packet.
// This is a blocking operation (i think)
void wait_for_packet() {
  while (Serial.available() < PACKET_LENGTH) {}
}

// Note that these serial objects are pointers so they can be passed around and reassigned easily

//#define MAX_SEQNUM (0xff)  //upper bound of seqnum, inclusive
//#define FIRST_SEQNUM (0x00) // initial sequence number
//
//u8 seqnum;
//
//// Increment the global sequence number
//void inc_seqnum() {
//  switch (seqnum) {
//    case MAX_SEQNUM:
//      seqnum = FIRST_SEQNUM;
//      break;
//    default:
//      seqnum++;
//      break;
//  }
//}

// Deserialize a packet object to the given pointer. Returns 0 on sucess and >0 on failure.
// Blocks until serial buffer contains an entire packet worth of bytes.
int get_packet(packet *p) {
  wait_for_packet();
  byte cmd_byte = Serial.read();
  byte value1_byte = Serial.read();
  byte value2_byte = Serial.read();
  byte seqnum_chksum_byte = Serial.read();
//  blink_delay(15);
  create_packet(p, cmd_byte, value1_byte, value2_byte, seqnum_chksum_byte);
  return 0;
}

// Send the packet over a serial interface
int send_packet(packet p) {
  Serial.write(p.cmd);
  Serial.write(p.value1);
  Serial.write(p.value2);
  Serial.write(p.seqnum_chksum);
  Serial.flush();
  return 0;
}

#endif
