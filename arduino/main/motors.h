#ifndef MOTORS_H
#define MOTORS_H

#include  "settings.h"
#include "Servo.h"

//#define MOTOR_MAX_AMP   (295) // theoretically 400
#define MOTOR_JERK_MAX  (20)
#define MOTOR_DELTA_MS  (50)
#define MOTOR_SETUP_WAIT_MS (200)

#define ESC_MIN_US      (1100)
#define ESC_CENTER_US   (1500)
#define ESC_MAX_US      (1900)
#define ESC_DEADBAND    (25 + ESC_DEADBAND_CUSTOM)  // +/- 25 region around 1500 that does nothing
#define ESC_DEADBAND_CUSTOM   (25)

#define COMS_CENTER (127)
#define THRUSTER_CENTER (0)

#define GOV_DELTA (127)
#define GOV_MAX (GOV_DELTA)
#define GOV_MIN (-GOV_DELTA)

#define MOTOR_INPUT_DELTA (2)

//--Motor Codes:-----------------------------
// Must be kept from 0-5 for iterative loops loops
//#define MOTOR_1 (0)
//#define MOTOR_2 (1)
//#define MOTOR_3 (2)
//#define MOTOR_4 (3)
//#define MOTOR_5 (4)
//#define MOTOR_6 (5)

#define NUM_MOTORS (6)

//--Pinouts:---------------------------------
// Thrusters:
#ifdef PROCESSOR_TEENSY_3_2
#warning Using Teensy motor pins
#define MOTOR_1_PIN (3)
#define MOTOR_2_PIN (4)
#define MOTOR_3_PIN (5)
#define MOTOR_4_PIN (6)
#define MOTOR_5_PIN (9)
#define MOTOR_6_PIN (10)
#else
// Arduino
#define MOTOR_1_PIN (8)
#define MOTOR_2_PIN (9)
#define MOTOR_3_PIN (10)
#define MOTOR_4_PIN (11)
#define MOTOR_5_PIN (12)
#define MOTOR_6_PIN (13)

#endif
int motor_pins[NUM_MOTORS] = {
  MOTOR_1_PIN, 
  MOTOR_2_PIN,
  MOTOR_3_PIN, 
  MOTOR_4_PIN,
  MOTOR_5_PIN, 
  MOTOR_6_PIN}; 

Servo motors[NUM_MOTORS];

void write_thruster(int thruster_index, int esc_us) {

  motors[thruster_index].writeMicroseconds(esc_us);
}

int translate_motor_val(int val2) {
  return (val2 * 3 + 1245);
}

void motor_setup() {
  // attach motors to pins
  for (int i = 0; i < NUM_MOTORS; i++) {
    motors[i].attach(motor_pins[i]);
  }
  
  delay(MOTOR_SETUP_WAIT_MS);

  // Initialize motor base values
  for (int i = 0; i < NUM_MOTORS; i++) {
    write_thruster(i, ESC_CENTER_US);
  }
}

#endif
