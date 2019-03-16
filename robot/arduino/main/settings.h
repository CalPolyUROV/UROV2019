#ifndef SETTINGS_H
#define SETTINGS_H

#define DEBUG false
/* Whether to output information on debug serial line.
   This may consume a lot of time away from the main coms or confuse them if they are the same interface.
*/

#define COMS_BAUD 9600

//--Motor Codes:-----------------------------
// Must be kept from 0-5 because of for loops
#define MOTOR_A (0)
#define MOTOR_B (1)
#define MOTOR_C (2)
#define MOTOR_D (3)
#define MOTOR_E (4)
#define MOTOR_F (5)

#define NUM_MOTORS (6)

//--Pinouts:---------------------------------
// Thrusters
// Mega Pins:
#define MOTOR_A_PIN 8
#define MOTOR_B_PIN 9
#define MOTOR_C_PIN 10
#define MOTOR_D_PIN 11
#define MOTOR_E_PIN 12
#define MOTOR_F_PIN 13
//Teensy Pins:
//#define MOTOR_A_PIN 3
//#define MOTOR_B_PIN 4
//#define MOTOR_C_PIN 5
//#define MOTOR_D_PIN 6
//#define MOTOR_E_PIN 22
//#define MOTOR_F_PIN 23

// Motor directions
#define MOTOR_A_DIR 1
#define MOTOR_B_DIR 1
#define MOTOR_C_DIR 1
#define MOTOR_D_DIR 1
#define MOTOR_E_DIR 1
#define MOTOR_F_DIR 1

#endif
