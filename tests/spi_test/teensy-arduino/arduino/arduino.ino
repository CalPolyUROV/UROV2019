#include <SPI.h>

void setup() {
  // initialize serial output
  Serial.begin(9600);

  // initialize SPI with the following settings
  //  speedMaximum 4MHz
  //  dataOrder MSBFIRST
  //  dataMode SPI_MODE0
  //    (clock polarity 0, clock phase 0, clock edge 1)
  //    (may need to change)
//  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE3));
  SPI.begin();
  delay(100);

  // initialize SS to deselected (active low)
  digitalWrite(SS, HIGH);
  
  Serial.println("Master initialized");
}

void loop() {
  // put your main code here, to run repeatedly:
  
  
  Serial.println("enabling SS");
  digitalWrite(SS, LOW);
  
  Serial.println("transmitting 1...");
  SPI.transfer(1);
  Serial.println("  sent 1");

  Serial.println("disabling SS");
  digitalWrite(SS, HIGH);
  
  delay(100);  
}
