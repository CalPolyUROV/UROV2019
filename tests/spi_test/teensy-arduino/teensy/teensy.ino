#include <SPI.h>

#define SCK_PIN   13  // D13 = pin19 = PortB.5
#define MISO_PIN  12  // D12 = pin18 = PortB.4
#define MOSI_PIN  11  // D11 = pin17 = PortB.3
#define SS_PIN    10  // D10 = pin16 = PortB.2


void slave_setup() {
  pinMode(SCK_PIN, INPUT);
  pinMode(MOSI_PIN, INPUT);
  pinMode(MISO_PIN, OUTPUT);
  pinMode(SS_PIN, INPUT);

  /*  Setup SPI control register SPCR
  SPIE - Enables the SPI interrupt when 1
  SPE - Enables the SPI when 1
  DORD - Sends data least Significant Bit First when 1, most Significant Bit first when 0
  MSTR - Sets the Arduino in master mode when 1, slave mode when 0
  CPOL - Sets the data clock to be idle when high if set to 1, idle when low if set to 0
  CPHA - Samples data on the trailing edge of the data clock when 1, leading edge when 0
  SPR1 and SPR0 - Sets the SPI speed, 00 is fastest (4MHz) 11 is slowest (250KHz)   */

  // enable SP Control Register at 4MHz
  SPCR = (0<<SPIE)|(1<<SPE)|(0<<DORD)|(0<<MSTR)|(0<<CPOL)|(0<<CPHA)|(0<<SPR1)|(0<<SPR0); 
  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  slave_setup();
  delay(10);
}

void loop() {
  // put your main code here, to run repeatedly:
//  Serial.println("teensy");
//  delay(100);
  unsigned char message;

  Serial.println("slave select DISABLED");
  
  // wait until SS is activated (active low)
  while(digitalRead(SS_PIN) == 1) {}
  // print confirmation
  Serial.println("slave select ACTIVE");
  
  // SPI ON
  SPCR = (1<<SPE)|(0<<DORD)|(0<<MSTR)|(0<<CPOL)|(0<<CPHA)|(0<<SPR1)|(0<<SPR0);
  // check status until data available
  while(!(SPSR & (1<<SPIF)));
  message = SPDR;
  // SPI OFF
  SPCR = (0<<SPE)|(0<<DORD)|(0<<MSTR)|(0<<CPOL)|(0<<CPHA)|(0<<SPR1)|(0<<SPR0);
  Serial.print("received byte ");
  Serial.println(message);
  
}
