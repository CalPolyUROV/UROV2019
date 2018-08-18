/*
  Based on http://www.arduino.cc/en/Tutorial/SerialCallResponse
  "This program sends an ASCII A (byte of value 65) on startup and repeats that
  until it gets some data in. Then it waits for a byte in the serial port, and
  sends three sensor values whenever it gets a byte in."

*/

#include "settings.h"
#include "defs.h"

/* The Teensy and Arduino use a different class for serial.
   If Arduino, Serial is a HardwareSerial
   If Teensy, Serial is a usb_serial_class
   This is done so the sepcific serial port is selectable.
    https://electronics.stackexchange.com/questions/58386/how-can-i-detect-which-arduino-board-or-which-controller-in-software
*/

SERIAL_CLASS *coms_serial;
DEBUG_SERIAL_CLASS *debug_serial;

// TODO: add debug serial port and utilize
// HardwareSerial *debug_serial;

byte recv_byte = 0;         // incoming serial byte

void setup() {

  coms_serial = &Serial; // This is USB serial
  coms_serial->begin(COMS_BAUD);
  while (!coms_serial) {
    ;
  }

  debug_serial = &Serial; // This is USB serial
  //debug_serial.begin(DEBUG_BAUD);

  establishContact();  // send a byte to establish contact until receiver responds
}

void loop() {
  // if we get a valid byte, read analog ins:
  if (coms_serial->available() > 0) {
    // get incoming byte:
    recv_byte = coms_serial->read();
    // read first analog input, divide by 4 to make the range 0-255:
    //firstSensor = analogRead(A0) / 4;
    // delay 10ms to let the ADC recover:
    delay(10);

  }
}

int establishContact() {
  struct packet p;
  if (get_packet(&p, -1)) {
    //error from get_packet()
    debug_packet(p);
  }
  if (p.cmd == EST_CON_CMD &&
      p.value1 == 0 &&
      p.value2 == 0 &&
      extract_seqnum(&p) == 0){
        return 0;
      }
      return 1;
}

int get_packet(struct packet* p, byte prev_seqnum) {
  p->cmd = coms_serial->read();
  p->value1 = coms_serial->read();
  p->value2 = coms_serial->read();
  p->seqnum_chksum = coms_serial->read();
  
  if (extract_chksum(p) != calc_chksum(p)) {
    // checksum failed
    // debug print result
    return 1;
  }
  if (!((extract_seqnum(p) == prev_seqnum + 1) |
        ((prev_seqnum == MAX_SEQNUM) && (extract_seqnum == FIRST_SEQNUM)))) {
    // incorrect seqnum
    // debug print result
    return 1;
  }
  return 0;
}

void debug_packet(struct packet p) {
  if (DEBUG) {
    debug_serial->print("cmd: ");
    debug_serial->println(p.cmd);
    debug_serial->print("value1: ");
    debug_serial->println(p.value1);
    debug_serial->print("value2: ");
    debug_serial->println(p.value2);
    debug_serial->print("seq_num: ");
    debug_serial->println(extract_seqnum(&p));
    debug_serial->print("seq_num: ");
    debug_serial->println(extract_chksum(&p));
  }
}

// Mask off the first 4 bits of the seqnum_chksum byte to get the chksum nibble
byte extract_chksum(struct packet* p) {
  return p->seqnum_chksum & CHKSUM_MASK;
}

// Bitshift the seqnum_chksum byte right 4 times to leave just the seqnum nibble
byte extract_seqnum(struct packet* p) {
  return p->seqnum_chksum >> 4;
}

// calculate the checksum value for a packet
byte calc_chksum(struct packet* p) {
  return (p->cmd + (p->value1 * 3) + (p->value2 * 5) + (extract_seqnum(p) * 7)) & CHKSUM_MASK;
}

