#ifndef __CAMERAS_H__
#define __CAMERAS_H__

#include "defs.h"
#include "settings.h"

void camera_setup(){
  pinMode(CAMERA_MUX_PIN_1, OUTPUT);
  pinMode(CAMERA_MUX_PIN_2, OUTPUT);
  pinMode(CAMERA_MUX_PIN_3, OUTPUT);

  
  digitalWrite(CAMERA_MUX_PIN_1, LOW);
  digitalWrite(CAMERA_MUX_PIN_2, LOW);
  digitalWrite(CAMERA_MUX_PIN_3, HIGH);
}

void set_camera(int i){
  int a = LOW;
  int b = LOW;
  int c = LOW;
  if (i & BIT0){
    a = HIGH;
  }
  if (i & BIT1){
    b = HIGH;
  }
  if (i & BIT2){
    c = HIGH;
  }
  digitalWrite(CAMERA_MUX_PIN_1, a);
  digitalWrite(CAMERA_MUX_PIN_2, b);
  digitalWrite(CAMERA_MUX_PIN_3, c);
}

#endif
