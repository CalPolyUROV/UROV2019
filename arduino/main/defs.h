#ifndef DEFS_H
#define DEFS_H

/* The Teensy and Arduino use a different class for serial.
   If Arduino, Serial is a HardwareSerial
   If Teensy, Serial is a usb_serial_class
   This is done so the sepcific serial port is selectable.
    https://electronics.stackexchange.com/questions/58386/how-can-i-detect-which-arduino-board-or-which-controller-in-software
*/

typedef unsigned char u8;

#define BIT0 0x01
#define BIT1 0x02
#define BIT2 0x04

#endif
