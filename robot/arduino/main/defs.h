// defs

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

