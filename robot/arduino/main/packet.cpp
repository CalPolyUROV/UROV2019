#include "packet.h"
#include "TeensyThreads.h"

// Wait for the UART buffer to be filled with a whole packet.
// This is a blocking operation (i think)
void wait_for_packet(SERIAL_CLASS *serial) {
  while (serial->available() < PACKET_LENGTH) {}
}

// Take values for a packet and place at a pointer, add checksum
void create_packet(packet *p, byte cmd, byte value1, byte value2, byte seqnum_nibble) {
  p->cmd = cmd;
  p->value1 = value1;
  p->value2 = value2;
  p->seqnum_chksum = (seqnum_nibble << 4) +  calc_chksum(cmd, value1, value2, seqnum_nibble);
}

// Send the packet over a serial interface
int send_packet(SERIAL_CLASS *serial, packet p) {
  threads.stop();
  serial->write(p.cmd);
  serial->write(p.value1);
  serial->write(p.value2);
  serial->write(p.seqnum_chksum);
  threads.start();
  return 0;
}

// Mask off the first 4 bits of the seqnum_chksum byte to get the chksum nibble
byte extract_chksum(byte seqnum_chksum) {
  return seqnum_chksum & CHKSUM_MASK;
}

// Bitshift the seqnum_chksum byte right 4 times to leave just the seqnum nibble
byte extract_seqnum(byte b) {
  return b >> 4; // is this wrong?
}

// calculate the checksum for values being put into a packet
byte calc_chksum(byte cmd, byte value1, byte value2, byte seqnum_nibble) {
  return (cmd +
          (value1 * 3) +
          (value2 * 5) +
          (seqnum_nibble * 7))
         & CHKSUM_MASK;
}

/* not used right now

  byte recalc_chksum(struct packet *p) {
  return calc_chksum(p->cmd, p->value1, p->value2, p->seqnum_chksum >> 4);
  }
*/
