#ifndef VECTOR_MOTOR_H
#define VECTOR_MOTOR_H

void motorSetup();
void setMotors(int X,int Y,int Z,int R,unsigned char buttons);
int brownOutPrevent(int currentSpeed, int targetSpeed);

#endif
