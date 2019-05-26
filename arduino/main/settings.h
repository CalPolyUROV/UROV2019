#ifndef SETTINGS_H
#define SETTINGS_H

#define COMS_BAUD 9600

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
// Thrusters:
#define MOTOR_1_PIN (8)
#define MOTOR_2_PIN (8)
#define MOTOR_3_PIN (10)
#define MOTOR_4_PIN (11)
#define MOTOR_5_PIN (12)
#define MOTOR_6_PIN (13)

#define CAMERA_MUX_PIN_1 (5)
#define CAMERA_MUX_PIN_2 (6)
#define CAMERA_MUX_PIN_3 (7)


// Motor directions
// For switching motor direction based on 3-phase wiring to match thruster orientation
#define MOTOR_1_DIR (-1)
#define MOTOR_2_DIR (1)
#define MOTOR_3_DIR (1)
#define MOTOR_4_DIR (1)
#define MOTOR_5_DIR (-1)
#define MOTOR_6_DIR (1)

#endif
