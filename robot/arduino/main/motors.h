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
#define ESC_DEADBAND    (25)  // +/- 25 region around 1500 that does nothing


#define MOTOR_INPUT_CENTER (127)
#define MOTOR_INPUT_MAX (255)
#define MOTOR_INPUT_MIN (0)

#define GOV_DELTA (127)
#define GOV_MAX (MOTOR_INPUT_CENTER + GOV_DELTA)
#define GOV_MIN (MOTOR_INPUT_CENTER - GOV_DELTA)

#define MOTOR_INPUT_DELTA (2)

struct Thruster {
  int current_value;
  volatile int target_value;
  int direction;
};


Thruster thrusters[NUM_MOTORS];
Servo motors[NUM_MOTORS];

int apply_governor(int input) {
  if (input > GOV_MAX) {
    return GOV_MAX;
  } else if (input < GOV_MIN) {
    return GOV_MIN;
  } else {
    return input;
  }
}

int apply_deadzone(int speed) {
  if ((speed > (ESC_CENTER_US - ESC_DEADBAND)) && (speed < (ESC_CENTER_US + ESC_DEADBAND))) {
    return ESC_CENTER_US;
  }
  else {
    return speed;
  }
}

int map_esc_speed(int input_speed) {
  int speed = ((input_speed - MOTOR_INPUT_CENTER) * 3) + ESC_CENTER_US;

  if (speed > ESC_MAX_US) {
    speed = ESC_MAX_US;
  }
  else if (speed < ESC_MIN_US) {
    speed = ESC_MIN_US;
  }
  speed = apply_deadzone(speed);

  return speed;
}

void set_motor_target(int thruster_index, int input) {
  int input_speed = apply_governor(input);

  int speed = map_esc_speed(input_speed);
  
//  if (thruster_index == 0) {
//    Serial.print(input);
//    Serial.print(" -> target: ");
//    Serial.println(speed);
//  }
  
  thrusters[thruster_index].target_value = speed;
}

void write_thruster(int thruster_index, int esc_speed) {

  motors[thruster_index].writeMicroseconds(esc_speed);
}

void update_motor(int thruster_index) {
  int current = thrusters[thruster_index].current_value;
  int target = thrusters[thruster_index].target_value;
  // Update current_value to be closer to target value
  if (target < current) {
    current = max(target, current - MOTOR_JERK_MAX);
  }
  else {
    current = min(target, current + MOTOR_JERK_MAX);
  }
  //  motors[thruster_index].write(120);//(motor->current_value * motor->direction) + ESC_CENTER_US);

  write_thruster(thruster_index, current);

  thrusters[thruster_index].current_value = current;
  thrusters[thruster_index].target_value = target;
}

// Updates all motors to move toward their target values
// Assumes only called after a safe time delay
void update_motors() {
  for (int thruster_index = 0; thruster_index < NUM_MOTORS; thruster_index++) {
    update_motor(thruster_index);
  }
}

void motorSetup() {
  // attach motors to pins
  motors[0].attach(MOTOR_A_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[1].attach(MOTOR_B_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[2].attach(MOTOR_C_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[3].attach(MOTOR_D_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[4].attach(MOTOR_E_PIN);//, ESC_MIN_US, ESC_MAX_US);
  motors[5].attach(MOTOR_F_PIN);//, ESC_MIN_US, ESC_MAX_US);

  delay(SETUP_WAIT_MS);

  thrusters[0].direction = MOTOR_A_DIR;
  thrusters[1].direction = MOTOR_B_DIR;
  thrusters[2].direction = MOTOR_C_DIR;
  thrusters[3].direction = MOTOR_D_DIR;
  thrusters[4].direction = MOTOR_E_DIR;
  thrusters[5].direction = MOTOR_F_DIR;

  // Initialize motor base values
  for (int i = 0; i < NUM_MOTORS; i++) {
    thrusters[i].current_value = ESC_CENTER_US;
    thrusters[i].target_value = ESC_CENTER_US;
  }

  // Update motors with initial values
  update_motors();

  delay(SETUP_WAIT_MS);
}

#endif
