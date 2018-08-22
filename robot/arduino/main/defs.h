#ifndef DEFS_H
#define DEFS_H

#include "settings.h"

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

#endif

