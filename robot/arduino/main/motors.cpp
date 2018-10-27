#include "motors.h"
#include "settings.h"

#define MOTOR_MAX_AMP   295
#define MOTOR_JERK_MAX  10
#define ESC_CENTER_MS   1500
#define ESC_MAX_MS      ESC_CENTER_MS + MOTOR_MAX_AMP
#define ESC_MIN_MS      ESC_CENTER_MS - MOTOR_MAX_AMP

// Global Motor Values
int current_speed_A = 0;
int current_speed_B = 0;
int current_speed_C = 0;
int current_speed_D = 0;
int current_speed_E = 0;
int current_speed_F = 0;

int target_speed_A = 0;
int target_speed_B = 0;
int target_speed_C = 0;
int target_speed_D = 0;
int target_speed_E = 0;
int target_speed_F = 0;

Servo motorA;
Servo motorB;
Servo motorC;
Servo motorD;
Servo motorE;
Servo motorF;

void motorSetup() {
   // attach motors to pins
   motorA.attach(MOTOR_A_PIN);
   motorB.attach(MOTOR_B_PIN);
   motorC.attach(MOTOR_C_PIN);
   motorD.attach(MOTOR_D_PIN);
   motorE.attach(MOTOR_E_PIN);
   motorF.attach(MOTOR_F_PIN);

   // initialize motor values
   motorA.writeMicroseconds(ESC_CENTER_MS);
   motorB.writeMicroseconds(ESC_CENTER_MS);
   motorC.writeMicroseconds(ESC_CENTER_MS);
   motorD.writeMicroseconds(ESC_CENTER_MS);
   motorE.writeMicroseconds(ESC_CENTER_MS);
   motorF.writeMicroseconds(ESC_CENTER_MS);

   // delay to ensure signal reception
   delay(100);
}

// assumes values are safe as far as acceleration
void setMotor(byte motor, byte value) {
   switch(motor) {
      case MOTOR_CODE_A:
         motorA.writeMicroseconds(map(value, MOTOR_A_DIR * 0, MOTOR_A_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      case MOTOR_CODE_B:
         motorB.writeMicroseconds(map(value, MOTOR_B_DIR * 0, MOTOR_B_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      case MOTOR_CODE_C:
         motorA.writeMicroseconds(map(value, MOTOR_C_DIR * 0, MOTOR_C_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      case MOTOR_CODE_D:
         motorA.writeMicroseconds(map(value, MOTOR_D_DIR * 0, MOTOR_D_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      case MOTOR_CODE_E:
         motorA.writeMicroseconds(map(value, MOTOR_E_DIR * 0, MOTOR_E_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      case MOTOR_CODE_F:
         motorA.writeMicroseconds(map(value, MOTOR_F_DIR * 0, MOTOR_F_DIR * 255, ESC_MIN_MS, ESC_MAX_MS));
         break;
      default:
         // invalid motor parameter
         // TODO: raise some sort of error?
         break;
   }
}
