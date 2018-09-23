#ifndef DEFS_H
#define DEFS_H

#include "settings.h"

/* The Teensy and Arduino use a different class for serial.
   If Arduino, Serial is a HardwareSerial
   If Teensy, Serial is a usb_serial_class
   This is done so the sepcific serial port is selectable.
    https://electronics.stackexchange.com/questions/58386/how-can-i-detect-which-arduino-board-or-which-controller-in-software
*/

// Select hardware
#ifdef MEGA
//Mega 2560 specific code
#warning "Arduino selected"
#define SERIAL_CLASS HardwareSerial

#elif defined(TEENSY) // Teensy specific
#warning "Teensy Selected"
// On Teensy, the USB port is usb_serial_class and GPIO serial is HardwareSerial (i think)
#define SERIAL_CLASS usb_serial_class

#else
#warning "Hardware selection failed"
#error "Unsupported hardware"
#endif

// TODO: handle debug serial selection. Debug channel is hardcoded mirror of coms for now
#define DEBUG_SERIAL_CLASS SERIAL_CLASS

#define LOWER_NIBBLE_MASK B00001111

#endif

