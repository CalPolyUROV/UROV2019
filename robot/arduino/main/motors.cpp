#include "motors.h"
#include "settings.h"
#include "TeensyThreads.h"

Servo motorA;
Servo motorB;
Servo motorC;
Servo motorD;
Servo motorE;
Servo motorF;

ServoMotor servoMotors[NUM_MOTORS];

void motorSetup() {
   // attach motors to pins
   motorA.attach(MOTOR_A_PIN);
   motorB.attach(MOTOR_B_PIN);
   motorC.attach(MOTOR_C_PIN);
   motorD.attach(MOTOR_D_PIN);
   motorE.attach(MOTOR_E_PIN);
   motorF.attach(MOTOR_F_PIN);

   // Add servos to array
   servoMotors[0].servo = &motorA;
   servoMotors[1].servo = &motorB;
   servoMotors[2].servo = &motorC;
   servoMotors[3].servo = &motorD;
   servoMotors[4].servo = &motorE;
   servoMotors[5].servo = &motorF;

   servoMotors[0].direction = MOTOR_A_DIR;
   servoMotors[1].direction = MOTOR_B_DIR;
   servoMotors[2].direction = MOTOR_C_DIR;
   servoMotors[3].direction = MOTOR_D_DIR;
   servoMotors[4].direction = MOTOR_E_DIR;
   servoMotors[5].direction = MOTOR_F_DIR;
   
   // Initialize motor base values
   for(int i = 0; i < NUM_MOTORS; i++) {
      servoMotors[i].current_value = ESC_CENTER_MS;
      servoMotors[i].target_value = ESC_CENTER_MS;
   }

   // Update motors with initial values
   updateMotors();
}

// Updates all motors to move toward their target values
// Assumes only called after a safe time delay
void updateMotors() {
   for(int i = 0; i < NUM_MOTORS; i++) {
      ServoMotor* curServo = &servoMotors[i];
      // Update current_value to be closer to target value
      if(curServo->target_value < curServo->current_value) {
         curServo->current_value -= max(curServo->target_value, curServo->current_value - MOTOR_JERK_MAX);
      }
      else {
         curServo->current_value -= min(curServo->target_value, curServo->current_value + MOTOR_JERK_MAX);
      }
      // Write new current_value out to motor
      threads.stop();
      (*(curServo->servo)).writeMicroseconds(
            map(curServo->current_value, 0, curServo->direction * 255, ESC_MIN_MS, ESC_MAX_MS)
      );
      threads.start();
   }
}

void setMotorTarget(byte motor, byte targetValue) {
   servoMotors[motor].target_value = (int)targetValue;
}
