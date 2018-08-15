/*
  Based on http://www.arduino.cc/en/Tutorial/SerialCallResponse
  "This program sends an ASCII A (byte of value 65) on startup and repeats that
  until it gets some data in. Then it waits for a byte in the serial port, and
  sends three sensor values whenever it gets a byte in."

*/
// settings
// TODO: move to settings.h
#define SERIAL_SELECTION USB_SERIAL
#define COMS_BAUD 9600

// defs
// TODO: move to defs.h
#define USB_SERIAL 1
#define SERIAL_2 2

#define CHKSUM_MASK B00001111
#define MAX_SEQNUM B00001111
#define FIRST_SEQNUM B00000000

//LUT
// lookup table for indexes of commands
// TODO: move to another file
// byte cmd_lut[255] = {EST_CMD, SET_MOT_CMD, READ...}
// currently using switch statement and bodge LUT, should still be moved to other file
#define EST_CON_CMD 0x00
#define SET_MOT_CMD 0x20
#define RD_SENS_CMD 0x40

struct packet {
  byte cmd;
  byte value1, value2;
  byte seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};

usb_serial_class *coms_serial;
// TODO: add debug serial port and utilize
// HardwareSerial *debug_serial;

byte recv_byte = 0;         // incoming serial byte

void setup() {
  /*switch (SERIAL_SELECTION) {
    case USB_SERIAL:
      coms_serial = &Serial;
      break;
    case SERIAL_2:
      coms_serial = &Serial2;
      break;
  }
  */
  coms_serial = &Serial;
  coms_serial->begin(COMS_BAUD);
  while (!coms_serial) {
    ;
  }

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

