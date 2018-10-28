// NOTE: THIS FILE IS NOT IN CURRENTLY USED BUT IS HERE FOR REFERENCE
//#include <wire.h>
#include <Servo.h>

#include "Arduino.h"
#include "VectorMotors.h"

#include "settings.h"

#define CHECK_BIT(var,pos) ((var) & (1<<(pos)))
#define MAX 295
#define MIN -MAX

//10 motor speed unit things per interval (maybe change to dv/dt later)

/* NEW PINOUT:
       +---------+
       | CAMERA  |
  +-------------------+
  |A||   FORWARD   ||B|
  +--|             |--+
  +--|             |--+
  |C||  VERTICAL   ||D|
  +--|             |--+
  +--|             |--+
  |E||  BACKWARD   ||F|
  +-------------------+
     | TETHER CONN |
     +-------------+
*/

///////////connecting the ESC to the arduino (switch the pin to the one in use)

#define ESC_CENTER_MS 1500
#define MOTOR_JERK_MAX 10
/*
   connect three 24 gauge wires to the arduino (can power the arduino)
   the yellow wire is the signal wire (connect to any pin on the arduino)
   the red and black wires are power and ground, they can supple the arduino, but are not nessesary
   now for the three wires connected to the motor
   any combination works, if the motor turns the wrong way, switch two wires
   test the direction without the propellers!
*/

////////////globals

int previous_speed_A = 0;
int previous_speed_B = 0;
int previous_speed_E = 0;
int previous_speed_F = 0;
int previous_speed_Z = 0;

// final motorspeeds
int motor_speed_A;
int motor_speed_B;
int motor_speed_E;
int motor_speed_F;
int motor_speed_Z;

Servo motorA;
Servo motorB;
Servo motorE;
Servo motorF;
Servo motorC;
Servo motorD;

//attach ESCs to pins and set current to 0 Amps

void motorSetup()
{
  // make the pin act like a servo
  motorA.attach(MOTOR_A_PIN);
  motorB.attach(MOTOR_B_PIN);
  motorC.attach(MOTOR_C_PIN);
  motorD.attach(MOTOR_D_PIN);
  motorE.attach(MOTOR_E_PIN);
  motorF.attach(MOTOR_F_PIN);

  // set the ESC to 0 Amps (1500us +-25us is the center)
  motorA.writeMicroseconds(ESC_CENTER_MS);
  motorB.writeMicroseconds(ESC_CENTER_MS);
  motorC.writeMicroseconds(ESC_CENTER_MS);
  motorD.writeMicroseconds(ESC_CENTER_MS);
  motorE.writeMicroseconds(ESC_CENTER_MS);
  motorF.writeMicroseconds(ESC_CENTER_MS);

  delay(100); // ensure that the signal was recieved
}

///////////////////////////////////////////////////////////////////////////how to write motorspeeds
// function that takes input from MIN to MAX
////////how to use the motor
// servo.writeMicroseconds(number from 1100 to 1900)
// less than 1500 should be backward (limit 1500-MAX = 1205)
// more than 1500 should be forward  (limit 1500+MAX = 1795)

void motor_A(int mspeed)
{
  motorA.writeMicroseconds(map(mspeed, MOTOR_A_DIR * MIN, MOTOR_A_DIR * MAX, 1500+MIN, 1500+MAX));
}

void motor_B(int mspeed)
{
  motorB.writeMicroseconds(map(mspeed, MOTOR_B_DIR * MIN, MOTOR_B_DIR * MAX, 1500+MIN, 1500+MAX));
}

void motor_C(int mspeed)
{
  motorC.writeMicroseconds(map(mspeed, MOTOR_C_DIR * MIN, MOTOR_C_DIR * MAX, 1500+MIN, 1500+MAX));
}

void motor_D(int mspeed)
{
  motorD.writeMicroseconds(map(mspeed, MOTOR_D_DIR * MIN, MOTOR_D_DIR * MAX, 1500+MIN, 1500+MAX));
}

void motor_E(int mspeed)
{
  motorE.writeMicroseconds(map(mspeed, MOTOR_E_DIR * MIN, MOTOR_E_DIR * MAX, 1500+MIN, 1500+MAX));
}

void motor_F(int mspeed)
{
  motorF.writeMicroseconds(map(mspeed, (MOTOR_F_DIR * MIN), MOTOR_F_DIR * MAX, 1500+MIN, 1500+MAX));
}


// allow rotation and planar movement simultaniously (takes x y z and r, then sets motorspeeds)
void setMotors(int X, int Y, int Z, int R, unsigned char buttons)
{
  motor_speed_A = constrain(((Y + X) / 1)
                            + (R / 1), MIN, MAX);

  motor_speed_B = constrain(((Y - X) / 1)
                            - (R / 1), MIN, MAX);

  motor_speed_E = constrain((((-1 * Y) + X) / 1)
                            - (R / 1), MIN, MAX);

  motor_speed_F = constrain((((-1 * Y) - X) / 1)
                            + (R / 1), MIN, MAX);

  motor_speed_Z = constrain(Z, MIN, MAX);

  previous_speed_A = brownOutPrevent(previous_speed_A, motor_speed_A);
  previous_speed_B = brownOutPrevent(previous_speed_B, motor_speed_B);
  previous_speed_E = brownOutPrevent(previous_speed_E, motor_speed_E);
  previous_speed_F = brownOutPrevent(previous_speed_F, motor_speed_F);
  previous_speed_Z = brownOutPrevent(previous_speed_Z, motor_speed_Z);

  //limiting code end
  motor_A(previous_speed_A);
  motor_B(previous_speed_B);
  motor_E(previous_speed_E);
  motor_F(previous_speed_F);

  //if (CHECK_BIT(buttons, 1)){}
  motor_C(previous_speed_Z);
  motor_D(previous_speed_Z);

  if (DEBUG) {
   /* Serial.print("X: ");
    Serial.println(X);
    Serial.print("Y: ");
    Serial.println(Y);
    Serial.print("Z: ");
    Serial.println(Z);
    Serial.print("R: ");
    Serial.println(R);
    
    Serial.print("Motor A: ");
    Serial.println(motorA.attached());
    Serial.println(previous_speed_A);
    Serial.print("Motor B: ");
    Serial.println(motorB.attached());
    Serial.println(previous_speed_B);
    Serial.print("Motor E: ");
    Serial.println(motorE.attached());
    Serial.println(previous_speed_E);
    Serial.print("Motor F: ");
    Serial.println(motorF.attached());
    Serial.println(previous_speed_F); */
    Serial.print("Motor CD: ");
    Serial.println(motorC.attached());
    Serial.println(previous_speed_Z);
  }
}

int brownOutPrevent(int currentSpeed, int targetSpeed)
{ // This jerk constraint can help prevent brownouts
  if ((targetSpeed - currentSpeed) > MOTOR_JERK_MAX)
  { //If target is over 10 above, only increase by 10
    return currentSpeed + MOTOR_JERK_MAX;
  }
  else if ((currentSpeed - targetSpeed) > MOTOR_JERK_MAX)
  { //If target is over 10 below
    return currentSpeed - MOTOR_JERK_MAX;
  }
  else
  { // it is okay to set to target
    return targetSpeed;
  }
}
