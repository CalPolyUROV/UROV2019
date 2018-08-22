/*
  Based on http://www.arduino.cc/en/Tutorial/SerialCallResponse
  "This program sends an ASCII A (byte of value 65) on startup and repeats that
  until it gets some data in. Then it waits for a byte in the serial port, and
  sends three sensor values whenever it gets a byte in."

*/

#include "settings.h"
#include "defs.h"
#include "packet.h"


SERIAL_CLASS *coms_serial; // Main UART coms to on-robot Raspberry Pi
DEBUG_SERIAL_CLASS *debug_serial; // Debug coms to connected PC?
// Note that these serial objects are pointers so they can be passed around and reassigned easily

// TODO: add debug serial port and utilize it
// HardwareSerial *debug_serial;

int seq_num; // Sequence number keeps track of packet order

void setup() {

  coms_serial = &Serial; // This is USB serial
  coms_serial->begin(COMS_BAUD);

  debug_serial = &Serial; // This is USB serial
  //debug_serial.begin(DEBUG_BAUD); // Doesn't need to be initialized again


  seq_num = 0; // TODO: Use FIRST_SEQNUM
  establishContact();  // send a byte to establish contact until receiver responds
}

void loop() {
  struct packet p;
  if (get_packet(&p, seq_num++)) {
    //error from get_packet()
    debug_packet(p);
  }
  debug_packet(p);
  handle_packet(p, seq_num++);
  delay(10);
}

void handle_packet(packet p, byte expect_seqnum_nibble) {
  struct packet response;
  switch (p.cmd) {
    case EST_CON_CMD:
      // TODO: bring in previous motor code from 2018
      create_packet(&response, EST_CON_ACK, p.value1, p.value2, expect_seqnum_nibble);
      break;
    case SET_MOT_CMD:
      // TODO: bring in previous motor code from 2018
      create_packet(&response, EST_CON_ACK, p.value1, p.value2, expect_seqnum_nibble);
      break;
    case RD_SENS_CMD:
      break;
    default:
      create_packet(&response, INV_CMD_ACK, p.value1, p.cmd, expect_seqnum_nibble);
      break;
  }
  send_packet(coms_serial, response);
}

// TODO: remove this? handle_packet() can handle this, just migrate seqnum checking
int establishContact() {
  struct packet p;
  if (get_packet(&p, FIRST_SEQNUM)) {
    //error from get_packet()
    debug_packet(p);
  }
  if (p.cmd == EST_CON_CMD &&
      p.value1 == 0 &&
      p.value2 == 0 &&
      extract_seqnum(p.seqnum_chksum) == 0) {
    return 0;
  }
  return 1;
}


// Deserialize a packet object to the given pointer. Returns 0 on sucess and >0 on failure.
// Blocks until serial buffer contains an entire packet worth of bytes.
int get_packet(packet *p, byte expect_seqnum_nibble) {
  wait_for_packet(coms_serial);
  byte cmd_byte = coms_serial->read();
  byte value1_byte = coms_serial->read();
  byte value2_byte = coms_serial->read();
  byte seqnum_chksum_byte = coms_serial->read();
  create_packet(p, cmd_byte, value1_byte, value2_byte, extract_seqnum(seqnum_chksum_byte));

  // check for correct check sum
  if (extract_chksum(seqnum_chksum_byte) != extract_chksum(p->seqnum_chksum)) {
    // checksum failed
    // debug print result
    return 1;
  }
  // Check squence number after checksum because seqnum of mangled packet is useless
  if (extract_seqnum(p->seqnum_chksum) != expect_seqnum_nibble) {
    // incorrect seqnum
    // debug print result
    return 2;
  }
  // Success
  return 0;
}

void debug_packet(packet p) {
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

