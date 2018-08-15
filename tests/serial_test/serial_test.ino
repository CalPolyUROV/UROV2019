#define INIT_CHAR '0'

char received = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  while (!Serial) {

  }
  establishContact();
}

void loop() {
  // put your main code here, to run repeatedly:

}

void establishContact() {
  while (Serial.available() <= 0) {}
  received = Serial.readBytes(&received, 1);
  if (received == INIT_CHAR) {
    Serial.print(INIT_CHAR);   // send a capital A
    delay(300);
  }
}

