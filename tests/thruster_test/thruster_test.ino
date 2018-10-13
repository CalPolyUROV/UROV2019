/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013
  by Scott Fitzgerald
  http://arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

#define MOTOR_PIN 12

#define ZERO 0
#define MAX 400
#define MIN -400
#define DELTA 10
#define WAIT 100

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = ZERO;    // variable to store the servo position

void setup()
{
  myservo.attach(MOTOR_PIN);  // attaches the servo on pin 9 to the servo object
}

void loop()
{
  for (pos = ZERO; pos <= MAX; pos += DELTA) // goes from 0 degrees to 180 degrees
  { // in steps of 1 degree
    write_servo(pos);             // tell servo to go to position in variable 'pos'
    delay(WAIT);                       // waits 15ms for the servo to reach the position
  }
  for (pos = MAX; pos >= MIN; pos -= DELTA) // goes from 180 degrees to 0 degrees
  {
    write_servo(pos);             // tell servo to go to position in variable 'pos'
    delay(WAIT);                      // waits 15ms for the servo to reach the position
  }
  for (pos = MIN; pos <= ZERO; pos += DELTA) {
    write_servo(pos);             // tell servo to go to position in variable 'pos'
    delay(WAIT);                       // waits 15ms for the servo to reach the position
  }
}

void write_servo(int val) {
  myservo.writeMicroseconds(1500 + val);
}
