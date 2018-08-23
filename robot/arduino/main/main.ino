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

// Sequence number keeps track of packet order
// Do not directly access or modify the global sequence number
// Always use the inc_seqnum() and get_seqnum_nibble() functions
uint8_t seqnum;

void setup() {

  coms_serial = &Serial; // This is USB serial
  coms_serial->begin(COMS_BAUD);

  debug_serial = coms_serial; // This is USB serial
  //debug_serial.begin(DEBUG_BAUD); // Doesn't need to be initialized again

  seqnum = 0; // TODO: Use FIRST_SEQNUM
  //establishContact();  // send a byte to establish contact until receiver responds
}

void loop() {
  struct packet p;
  if (get_packet(&p, get_seqnum_nibble())) {
    //error from get_packet()
  }
  inc_seqnum();
  debug_packet(debug_serial, p);
  handle_packet(p, seq_num++);
  delay(10);
}

void handle_packet(packet p, byte expect_seqnum_nibble) {
  struct packet response;
  switch (p.cmd) {
    case EST_CON_CMD:
      if ((p.value1 == EST_CON_VAL1) &
          (p.value2 == EST_CON_VAL2) &
          (extract_seqnum(p.seqnum_chksum) == FIRST_SEQNUM)) {
        create_packet(&response, EST_CON_ACK, p.value1, p.value2, expect_seqnum_nibble);
      }
      // Establish connection packet was not valid
      create_inv_packet(&response, p, expect_seqnum_nibble);
      break;
    case SET_MOT_CMD:
      // TODO: bring in previous motor code from 2018
      create_packet(&response, EST_CON_ACK, p.value1, p.value2, expect_seqnum_nibble);
      break;
    case RD_SENS_CMD:
      break;
    default:
      create_inv_packet(&response, p, expect_seqnum_nibble);
      break;
  }
  send_packet(coms_serial, response);
}

// function for prepping a response to an invalid packet, for when you want to say "NOPE"
void create_inv_packet(packet *response, packet p, byte seqnum_nibble) {
  create_packet(response, INV_CMD_ACK, p.value1, p.cmd, seqnum_nibble);
}

// TODO: remove this? handle_packet() can handle this, just migrate seqnum checking
/* int establishContact() {
  struct packet p;
  if (get_packet(&p, FIRST_SEQNUM)) {
    //error from get_packet()
    debug_packet(debug_serial, p);
  }
  if (p.cmd == EST_CON_CMD &&
      p.value1 == 0 &&
      p.value2 == 0 &&
      extract_seqnum(p.seqnum_chksum) == 0) {
    return 0;
  }
  return 1;
}
*/


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

// Increment the global sequence number
void inc_seqnum() {
  switch (seqnum) {
    case MAX_SEQNUM:
      seqnum = FIRST_SEQNUM;
      break;
    default:
      seqnum++;
      break;
  }
}

// Getter for global sequence number
byte get_seqnum_nibble() {
  return seqnum & LOWER_NIBBLE_MASK;
}

void debug_packet(DEBUG_SERIAL_CLASS *serial, packet p) {
  if (DEBUG) {
    serial->print("cmd: ");
    serial->println(p.cmd);

    serial->print("value1: ");
    serial->println(p.value1);

    serial->print("value2: ");
    serial->println(p.value2);

    serial->print("seq_num: ");
    serial->println(extract_seqnum(p.seqnum_chksum));

    serial->print("seq_num: ");
    serial->println(extract_chksum(p.seqnum_chksum));
  }
}

