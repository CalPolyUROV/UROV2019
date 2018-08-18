// defs

// Select hardware
#ifdef MEGA
//Mega 2560 specific code
#warning "Arduino selected"
#define SERIAL_CLASS HardwareSerial

#elif defined(TEENSY)
// Teensy specific
#warning "Teensy Selected"
#define SERIAL_CLASS usb_serial_class

#else
#warning "Hardware selection failed"
#error "Unsupported hardware"
#endif

#define DEBUG_SERIAL_CLASS SERIAL_CLASS

#define CHKSUM_MASK B00001111
#define MAX_SEQNUM B00001111
#define FIRST_SEQNUM B00000000

//LUT
// lookup table for indexes of commands
// byte cmd_lut[255] = {EST_CMD, SET_MOT_CMD, READ...}
// currently using switch statement and bodge LUT
#define EST_CON_CMD 0x00
#define SET_MOT_CMD 0x20
#define RD_SENS_CMD 0x40

struct packet {
  byte cmd;
  byte value1, value2;
  byte seqnum_chksum; // first 4 bits used for sequence number, second 4 used for checksum
};

#define TRUE 1
#define FALSE 0



