#ifndef SERIAL_H
#define SERIAL_H

#include "defs.h"
#include "settings.h"
#include "packet.h"
#include "blink.h"

void initialize_serial() {
  Serial.begin(COMS_BAUD);
  while (!Serial) {
    // wait for serial port to connect. Needed for native USB
  }
}

// Wait for the UART buffer to be filled with a whole packet.
// This is a blocking operation (i think)
void wait_for_packet() {
  while (Serial.available() < PACKET_LENGTH) {}
}

// Deserialize a packet object to the given pointer. Returns 0 on sucess and >0 on failure.
// Blocks until serial buffer contains an entire packet worth of bytes.
int get_packet(packet *p) {
  wait_for_packet();
  byte cmd_byte = Serial.read();
  byte value1_byte = Serial.read();
  byte value2_byte = Serial.read();
  create_packet(p, cmd_byte, value1_byte, value2_byte); //, seqnum_chksum_byte);
  return 0;
}

// Send the packet over a serial interface
int send_packet(packet p) {
  Serial.write(p.cmd);
  Serial.write(p.value1);
  Serial.write(p.value2);
  Serial.flush();
  return 0;
}

#endif
