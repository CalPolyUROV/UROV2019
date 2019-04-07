#ifndef SETTINGS_H
#define SETTINGS_H

#define DEBUG false
/* Whether to output information on debug serial line.
   This may consume a lot of time away from the main coms or confuse them if they are the same interface.
*/

#define COMS_BAUD 9600

//--Axis numbers-----------------------------
#define X_AXIS      (0)
#define Y_AXIS      (1)
#define Z_AXIS      (2)
#define YAW_AXIS    (3)
#define PITCH_AXIS  (4)
#define ROLL_AXIS   (5)

//--Motor Codes:-----------------------------
// Must be kept from 0-5 for iterative loops loops
#define MOTOR_1 (0)
#define MOTOR_2 (1)
#define MOTOR_3 (2)
#define MOTOR_4 (3)
#define MOTOR_5 (4)
#define MOTOR_6 (5)

#define NUM_MOTORS (6)

//--Pinouts:---------------------------------
// Thrusters
// Mega Pins:
#define MOTOR_1_PIN (8)
#define MOTOR_2_PIN (9)
#define MOTOR_3_PIN (10)
#define MOTOR_4_PIN (11)
#define MOTOR_5_PIN (12)
#define MOTOR_6_PIN (13)

//Teensy Pins:
//#define MOTOR_1_PIN (3)
//#define MOTOR_2_PIN (4)
//#define MOTOR_3_PIN (5)
//#define MOTOR_4_PIN (6)
//#define MOTOR_5_PIN (22)
//#define MOTOR_6_PIN (23)

// Motor directions
// For switching motor direction based on 3-phase wiring to match thruster orientation
#define MOTOR_1_DIR 1
#define MOTOR_2_DIR 1
#define MOTOR_3_DIR 1
#define MOTOR_4_DIR 1
#define MOTOR_5_DIR 1
#define MOTOR_6_DIR 1

#endif
