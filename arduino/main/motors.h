#ifndef MOTORS_H
#define MOTORS_H

//#include <PWMServo.h>
//#include <TeensyThreads.h>
#include <Servo.h>

#include  "settings.h"

//#define MOTOR_MAX_AMP   (295) // theoretically 400
#define MOTOR_JERK_MAX  (20)
#define MOTOR_DELTA_MS  (50)
#define SETUP_WAIT_MS (200)

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
//
//struct Thruster {
//  int current_value;
//  volatile int target_value;
//  int direction;
//};


//Thruster thrusters[NUM_MOTORS];
Servo motors[NUM_MOTORS];

void write_thruster(int thruster_index, int esc_us) {

  motors[thruster_index].writeMicroseconds(esc_us);
}

int translate_motor_val(int val2) {
  return (val2 * 3 + 1245);
}

void motor_setup() {
  // attach motors to pins
  motors[0].attach(MOTOR_1_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[1].attach(MOTOR_2_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[2].attach(MOTOR_3_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[3].attach(MOTOR_4_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[4].attach(MOTOR_5_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[5].attach(MOTOR_6_PIN);//, ESC_MIN_US, ESC_MAX_US);

  delay(SETUP_WAIT_MS);

  // Initialize motor base values
  for (int i = 0; i < NUM_MOTORS; i++) {
    write_thruster(i, ESC_CENTER_US);
  }
}

#endif
