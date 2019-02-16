#ifndef MOTORS_H
#define MOTORS_H

#include <PWMServo.h>
#include <TeensyThreads.h>

#include  "settings.h"

#define MOTOR_MAX_AMP   (295) // theoretically 400
#define MOTOR_JERK_MAX  (10)
#define MOTOR_DELTA_MS  (50)

#define ESC_MIN_MS      (1100)
#define ESC_CENTER_MS   (1500)
#define ESC_MAX_MS      (1900)
#define ESC_DEADBAND    (25)  // +/- 25 region around 1500 that does nothing

#define NUM_MOTORS      (6)

struct Motor {
  int current_value;
  volatile int target_value;
  PWMServo* servo;
  int direction;
};

PWMServo motorA;
PWMServo motorB;
PWMServo motorC;
PWMServo motorD;
PWMServo motorE;
PWMServo motorF;

Motor motors[NUM_MOTORS];


void setMotorTarget(byte motor, byte targetValue) {
  motors[motor].target_value = (int)targetValue;
}
// Updates all motors to move toward their target values
// Assumes only called after a safe time delay
//void updateMotors() {
//  for (int i = 0; i < NUM_MOTORS; i++) {
//    Motor *motor = &motors[i];
//    // Update current_value to be closer to target value
//    if (motor->target_value < motor->current_value) {
//      motor->current_value -= max(motor->target_value, motor->current_value - MOTOR_JERK_MAX);
//    }
//    else {
//      motor->current_value -= min(motor->target_value, motor->current_value + MOTOR_JERK_MAX);
//    }
//    // Write new current_value out to motor
//    threads.stop();
//    motor->servo->write(map(motor->current_value,
//                            0, motor->direction * 255,
//                            ESC_MIN_MS, ESC_MAX_MS)
//    );
//    threads.start();
//  }
//}

void updateMotors()
{
  for (int i = 0; i < NUM_MOTORS; i++)
  {
    Motor *motor = &motors[i];
    //checking if the current value is greater than desired value. Means we need to ramp down
    if (motor->target_value <  motor->current_value)    
    {
      // checking if the difference between two values is greater than the desired interval 
      if ((motor->target_value) - (motor->current_value) > MOTOR_JERK_MAX) 
      {
        // if the value of the two is greater than desired we slowly decrease current value by moter jerk max
        motor->current_value -= MOTOR_JERK_MAX;
      }
      else
      {
        // if the difference is less than motor jerk max than we can set current equal to target
        motor->current_value = motor->target_value;
      }
    }
    // if the target value is greater than current then we ramp up 
    else if ((motor->target_value) > (motor->current_value))
    {
      // if the difference between two values is greater than desired motor jerk max, than we slowly ramp up 
      if ((motor->target_value) - (motor->current_value) > MOTOR_JERK_MAX)
      {
        motor->current_value += MOTOR_JERK_MAX;
      }
      else
      {
        // if the difference between two values is less than motor jerk max than we can just set current to target 
        motor->current_value = motor->target_value;
      }
    }
  }
}

void writeMotors()
{
  for (int i = 0; i < NUM_MOTORS; i++)
  {
    Motor *motor = &motors[i];
    threads.stop();
    motor->servo->write(map(motor->current_value,
                            0, motor->direction * 255,
                            ESC_MIN_MS, ESC_MAX_MS)
                       );
    threads.start();
  }
}







void motorSetup() {
  // attach motors to pins
  motorA.attach(MOTOR_A_PIN, ESC_MIN_MS, ESC_MAX_MS);
  motorB.attach(MOTOR_B_PIN, ESC_MIN_MS, ESC_MAX_MS);
  motorC.attach(MOTOR_C_PIN, ESC_MIN_MS, ESC_MAX_MS);
  motorD.attach(MOTOR_D_PIN, ESC_MIN_MS, ESC_MAX_MS);
  motorE.attach(MOTOR_E_PIN, ESC_MIN_MS, ESC_MAX_MS);
  motorF.attach(MOTOR_F_PIN, ESC_MIN_MS, ESC_MAX_MS);

  // Add servos to array
  motors[0].servo = &motorA;
  motors[1].servo = &motorB;
  motors[2].servo = &motorC;
  motors[3].servo = &motorD;
  motors[4].servo = &motorE;
  motors[5].servo = &motorF;

  motors[0].direction = MOTOR_A_DIR;
  motors[1].direction = MOTOR_B_DIR;
  motors[2].direction = MOTOR_C_DIR;
  motors[3].direction = MOTOR_D_DIR;
  motors[4].direction = MOTOR_E_DIR;
  motors[5].direction = MOTOR_F_DIR;

  // Initialize motor base values
  for (int i = 0; i < NUM_MOTORS; i++) {
    motors[i].current_value = ESC_CENTER_MS;
    motors[i].target_value = ESC_CENTER_MS;
  }

  // Update motors with initial values
  updateMotors();
}

#endif
