#ifndef MOTORS_H
#define MOTORS_H

#define MOTOR_MAX_AMP   295
#define MOTOR_JERK_MAX  10
#define MOTOR_DELTA_MS  50
#define ESC_CENTER_MS   1500
#define ESC_MAX_MS      ESC_CENTER_MS + MOTOR_MAX_AMP
#define ESC_MIN_MS      ESC_CENTER_MS - MOTOR_MAX_AMP
#define NUM_MOTORS      6

#include <arduino.h>
#include <Servo.h>

struct ServoMotor {
   int current_value;
   volatile int target_value;
   Servo* servo;
   int direction;
};

void motorSetup();
void updateMotors();
void setMotorTarget(byte motor, byte targetValue);

#endif
