/* UART Example, any character received on either the real
   serial port, or USB serial (or emulated serial to the
   Arduino Serial Monitor when using non-serial USB types)
   is printed as a message to both ports.

   This example code is in the public domain.
*/

#define LED_PIN 13
// set this to the hardware serial port you wish to use
#define HWSERIAL Serial1

void setup() {

  pinMode(LED_PIN, OUTPUT);
  on();
  Serial.begin(9600);
//  get_AT_cmd();
  off();
}

void on() {
  digitalWrite(LED_PIN, HIGH); // turn the LED on (HIGH is the voltage level)
}

void off() {
  digitalWrite(LED_PIN, LOW); // turn the LED off by making the voltage LOW
}

void get_AT_cmd()
{
  byte incomingByte;
  if (Serial.available() > 2) {
    on();
    incomingByte = Serial.read();
    incomingByte = Serial.read();
    incomingByte = Serial.read();
    Serial.println("Got AT command");
  }
}
void loop() {
  int incomingByte;

  if (Serial.available() > 3) {
    on();
    incomingByte = Serial.read();
    Serial.print(incomingByte);
    incomingByte = Serial.read();
    Serial.print(incomingByte);
    incomingByte = Serial.read();
    Serial.print(incomingByte);
    incomingByte = Serial.read();
    Serial.print(incomingByte);
//    Serial.println();
//  delay(100);
    off();
  }
}
