
#include "Servo.h"

//Teensy pins: 3, 4, 5, 6, 9, 10/
#define MOTOR_PIN 3
#define MOTOR_PIN_2 4

#define ESC_CENTER_US (1500)
#define ESC_RANGE (150)
#define ESC_MAX_US (ESC_CENTER_US + ESC_RANGE)
#define ESC_MIN_US (ESC_CENTER_US - ESC_RANGE)
#define ESC_DEADZONE (25)

#define INPUT_CENTER (127)
#define INPUT_MAX (255)
#define INPUT_MIN (0)

#define GOV_DELTA (120)
#define GOV_MAX (INPUT_CENTER + GOV_DELTA)
#define GOV_MIN (INPUT_CENTER - GOV_DELTA)

#define DELTA (2)

#define WAIT_MS (250)

/* The maximum throttle value
   Originally, we would use 400 for this be it seemed to be having issues now
   295 has been working better
   ESC PWM Characteristics:
      Pulse-width   (PWM)
      Max Reverse:  1100 μs
      Stopped:      1500 μs
      Max Forward:  1900 μs
      Deadband:     1475-1525 μs

  The maximum change in motor speed
    25 is too high, causing voltage drops from 24V to 21V
    5 and 10 are much safer
*/

Servo thruster;  // create servo object to control a servo
Servo thruster_2;
// twelve servo objects can be created on most boards

int input = INPUT_CENTER;    // variable to store the servo position

void setup()
{
  Serial.begin(9600);
  Serial.println("Starting up");
  thruster.attach(MOTOR_PIN);  // attaches the servo on pin 9 to the servo object
  thurster_2.attach(MOTOR_PIN_2
  Serial.println("Attached");
  delay(WAIT_MS);
  thruster.writeMicroseconds(ESC_CENTER_US);
  thruster_2.writeMicroseconds(ESC_CENTER_US);
  Serial.println("Wrote initial signal");
  delay(WAIT_MS); // ensure that the signal was recieved
}

void loop()
{
  Serial.println("Starting Loop");
  for (input = INPUT_CENTER; input <= INPUT_MAX; input += DELTA) // goes from 0 degrees to 180 degrees
  { // in steps of 1 degree
    write_servo(input);
    delay(WAIT_MS);
  }
  for (input = INPUT_MAX; input >= INPUT_MIN; input -= DELTA) // goes from 180 degrees to 0 degrees
  {
    write_servo(input);
    delay(WAIT_MS);
  }
  for (input = INPUT_MIN; input <= INPUT_CENTER; input += DELTA) {
    write_servo(input);
    delay(WAIT_MS);
  }
}

int map_esc_speed(int input_speed) {
  input_speed = apply_max_input(input_speed);
  int speed = (input_speed - INPUT_CENTER) * 3;
  speed = ESC_CENTER_US + speed;
  return apply_deadzone(speed);
}

int apply_max_input(int input) {
  if (input > GOV_MAX) {
    return GOV_MAX;
  } else if (input < GOV_MIN) {
    return GOV_MIN;
  } else {
    return input;
  }
}

int apply_deadzone(int speed) {
  if ((speed > (ESC_CENTER_US - ESC_DEADZONE)) && (speed < (ESC_CENTER_US + ESC_DEADZONE))) {
    return ESC_CENTER_US;
  }
  else {
    return speed;
  }
}

void write_servo(int input) {
  int speed = map_esc_speed(input);
  Serial.print(input);
  Serial.print(" -> ");
  Serial.println(speed);
  Serial.flush();
  thruster.writeMicroseconds(speed);
  thruster_2.writeMicroseconds(speed);
}
