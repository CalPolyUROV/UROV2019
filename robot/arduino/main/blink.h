#define LED_PIN 13
#define DELAY 1000

void blink_setup(){
  // initialize the digital pin as an output.
  pinMode(LED_PIN, OUTPUT);
}

void on() {
  digitalWrite(LED_PIN, HIGH); // turn the LED on (HIGH is the voltage level)
}

void off() {
  digitalWrite(LED_PIN, LOW); // turn the LED off by making the voltage LOW
}

void blink_std() {
  on();
  delay(DELAY);
  off();
}

void blink_delay(int ms){
  on();
  delay(ms);
  off();
}
