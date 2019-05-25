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

struct Thruster {
  int current_value;
  volatile int target_value;
  int direction;
};


Thruster thrusters[NUM_MOTORS];
Servo motors[NUM_MOTORS];
//int axis[6] = {0, 0, 0, 0, 0, 0};

/*int apply_governor(int input) {
  if (input > GOV_MAX) {
    return GOV_MAX;
  } else if (input < GOV_MIN) {
    return GOV_MIN;
  } else {
    return input;
  }
  }*/

/*int apply_deadzone(int speed) {
  if ((speed > (ESC_CENTER_US - ESC_DEADBAND)) && (speed < (ESC_CENTER_US + ESC_DEADBAND))) {
    return ESC_CENTER_US;
  }
  else {
    return speed;
  }
  }*/

/*int map_esc_speed(int input_speed) {
  int speed = (input_speed * 3) + ESC_CENTER_US;
  if (speed > ESC_MAX_US) {
    speed = ESC_MAX_US;
  }
  else if (speed < ESC_MIN_US) {
    speed = ESC_MIN_US;
  }
  speed = apply_deadzone(speed);
  return speed;
  }*/


/*void set_motor_target(int thruster_index, int input) {
  // TODO: clamp target speed
  int input_speed = apply_governor(input);
  int speed = map_esc_speed(input_speed);
  thrusters[thruster_index].target_value = speed;
  }*/

/*void update_motor_target(int thruster_index) {
  switch (thruster_index) {
    // TODO: move logic out into another function to remove repeat code
    // TODO: switch to summing x, y, and yaw as simple control system
    case MOTOR_1:
      set_motor_target(MOTOR_1, axis[X_AXIS] + axis[Y_AXIS] - axis[YAW_AXIS]);
      break;
    case MOTOR_2:
      set_motor_target(MOTOR_2, -axis[X_AXIS] + axis[Y_AXIS] - axis[YAW_AXIS]);
      break;
    case MOTOR_3:
      set_motor_target(MOTOR_3, axis[Z_AXIS] + axis[ROLL_AXIS]);
      break;
    case MOTOR_4:
      set_motor_target(MOTOR_4, axis[Z_AXIS] - axis[ROLL_AXIS]);
      break;
    case MOTOR_5:
      set_motor_target(MOTOR_5, - axis[X_AXIS] + axis[Y_AXIS] + axis[YAW_AXIS]);
      break;
    case MOTOR_6:
      set_motor_target(MOTOR_6, axis[X_AXIS] + axis[Y_AXIS] + axis[YAW_AXIS]);
      break;
    default:
      // Panic
      break;
  }
  }*/

/*int trigger_motor_updates(int axis_index) {
  switch (axis_index) {
    // TODO: move logic out into another function to remove repeat code
    // TODO: switch to summing x, y, and yaw as simple control system
    case X_AXIS:
      update_motor_target(MOTOR_1);
      update_motor_target(MOTOR_2);
      update_motor_target(MOTOR_5);
      update_motor_target(MOTOR_6);
      break;
    case Y_AXIS:
      update_motor_target(MOTOR_1);
      update_motor_target(MOTOR_2);
      update_motor_target(MOTOR_5);
      update_motor_target(MOTOR_6);
      break;
    case Z_AXIS:
      update_motor_target(MOTOR_3);
      update_motor_target(MOTOR_4);
      break;
    case YAW_AXIS:
      update_motor_target(MOTOR_1);
      update_motor_target(MOTOR_2);
      update_motor_target(MOTOR_5);
      update_motor_target(MOTOR_6);
      break;
    case PITCH_AXIS:
      // Cannot be preformed by thruster config
      break;
    case ROLL_AXIS:
      //Not implemented on controller?
      update_motor_target(MOTOR_3);
      update_motor_target(MOTOR_4);
      break;
    default:
      // Panic
      break;
  }
  }*/

/*int set_axis(int axis_index, int input) {
  switch (axis_index) {
    case X_AXIS:
      axis[axis_index] = input;
      break;
    case Y_AXIS:
      axis[axis_index] = input;
      break;
    case Z_AXIS:
      axis[axis_index] = input;
      break;
    case YAW_AXIS:
      axis[axis_index] = input;
      break;
    case PITCH_AXIS:
      // Cannot be preformed by thruster config
      axis[axis_index] = input;
      break;
    case ROLL_AXIS:
      axis[axis_index] = input;
      break;
    default:
      // Panic
      break;
  }
  }*/
void write_thruster(int thruster_index, int esc_speed) {

  motors[thruster_index].writeMicroseconds(esc_speed);
}
//
//void update_motor_speed(int thruster_index) {
//  int current = thrusters[thruster_index].current_value;
//  int target = thrusters[thruster_index].target_value;
//  // Update current_value to be closer to target value
//  if (target < current) {
//    current = max(target, current - MOTOR_JERK_MAX);
//  }
//  else {
//    current = min(target, current + MOTOR_JERK_MAX);
//  }
//  motors[thruster_index].write(120);//(motor->current_value * motor->direction) + ESC_CENTER_US);
//
//  write_thruster(thruster_index, current);
//
//  thrusters[thruster_index].current_value = current;
//  thrusters[thruster_index].target_value = target;
//}
//
//// Updates all motors to move toward their target values
//// Assumes only called after a safe time delay
//void update_all_motors_speeds() {
//  //  for (int thruster_index = 0; thruster_index < NUM_MOTORS; thruster_index++) {
//  //    update_motor(thruster_index);
//  //  }
//  update_motor_speed(MOTOR_1);
//  update_motor_speed(MOTOR_2);
//  update_motor_speed(MOTOR_3);
//  update_motor_speed(MOTOR_4);
//  update_motor_speed(MOTOR_5);
//  update_motor_speed(MOTOR_6);
//}

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

  thrusters[0].direction = MOTOR_1_DIR;
  thrusters[1].direction = MOTOR_2_DIR;
  thrusters[2].direction = MOTOR_3_DIR;
  thrusters[3].direction = MOTOR_4_DIR;
  thrusters[4].direction = MOTOR_5_DIR;
  thrusters[5].direction = MOTOR_6_DIR;

  // Initialize motor base values
  for (int i = 0; i < NUM_MOTORS; i++) {
    thrusters[i].current_value = ESC_CENTER_US;
    thrusters[i].target_value = ESC_CENTER_US;
  }

  // Update motors with initial values
  // update_all_motors_speeds();

  delay(SETUP_WAIT_MS);
}

#endif
