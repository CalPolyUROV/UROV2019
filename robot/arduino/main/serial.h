#ifndef SERIAL_H
#define SERIAL_H

#include "defs.h"
#include "settings.h"

#define MAX_SEQNUM (0xff)  //upper bound of seqnum, inclusive
#define FIRST_SEQNUM (0x00) // initial sequence number

u8 seqnum;

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

#endif