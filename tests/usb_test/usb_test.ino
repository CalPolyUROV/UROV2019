/* UART Example, any character received on either the real
   serial port, or USB serial (or emulated serial to the
   Arduino Serial Monitor when using non-serial USB types)
   is printed as a message to both ports.

   This example code is in the public domain.
*/

#define LED_PIN 13

char cmd;
char val1;
char val2;
char zero;

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

void loop() {

  if (Serial.available() > 3) {
    on();
    cmd = Serial.read();
    val1 = Serial.read();
    val2 = Serial.read();
    zero = Serial.read();
    Serial.print(cmd);
    Serial.print(val1);
    Serial.print(val2);
    Serial.print(0);
    off();
  }
}
