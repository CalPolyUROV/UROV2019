#ifndef BLINK_H
#define BLINK_H

#define LED_PIN 13
#define BLINK_DELAY 750

void blink_setup() {
  // initialize the digital pin as an output.
  pinMode(LED_PIN, OUTPUT);
}

void led_on() {
  digitalWrite(LED_PIN, HIGH); // turn the LED on (HIGH is the voltage level)
}

void led_off() {
  digitalWrite(LED_PIN, LOW); // turn the LED off by making the voltage LOW
}

void blink_std() {
  led_on();
  delay(BLINK_DELAY);
  led_off();
}

void blink_delay(int ms) {
  led_on();
  delay(ms);
  led_off();
}


#endif
