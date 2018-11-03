
#include <SPI.h>

#define MOSI_PIN 11
#define MISO_pin 12
#define SCK_PIN 13
#define CS_PIN 15

void setup() {
  Serial.begin(9600);

  // start the SPI library:
  SPI.begin();

  // initalize the  data ready and chip select pins:
  pinMode(chipSelectPin, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:

  Serial.print(received);
}

void read_write(Packet p){
  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
  // take the chip select low to select the device:
  digitalWrite(chipSelectPin, LOW);

  SPI.transfer('r'); //Send register location

  // take the chip select high to de-select:
  digitalWrite(chipSelectPin, HIGH);
  // release control of the SPI port
  SPI.endTransaction();
}
