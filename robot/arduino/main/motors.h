#ifndef MOTORS_H
#define MOTORS_H

#include <arduino.h>
#include <Servo.h>

void motorSetup();
void setMotor(byte motor, byte value);

#endif
