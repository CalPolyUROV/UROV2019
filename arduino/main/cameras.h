#ifndef __CAMERAS_H__
#define __CAMERAS_H__

#include "defs.h"
#include "settings.h"

void camera_setup(){
  pinMode(CAMERA_MUX_PIN_1, OUTPUT);
  pinMode(CAMERA_MUX_PIN_2, OUTPUT);
  pinMode(CAMERA_MUX_PIN_3, OUTPUT);
}

void set_camera(int i){
  int a = (i & BIT0) ? HIGH : LOW;
  int b = (i & BIT1) ? HIGH : LOW;
  int c = (i & BIT2) ? HIGH : LOW;
  digitalWrite(CAMERA_MUX_PIN_1, a);
  digitalWrite(CAMERA_MUX_PIN_2, b);
  digitalWrite(CAMERA_MUX_PIN_3, c);
}

#endif
