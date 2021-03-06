
#include "settings.h"
#include "defs.h"
#include "serial.h"
#include "packet.h"
//#include "blink.h"
#include "motors.h"
#include "cameras.h"

packet p;

void setup() {
    initialize_serial();
 
  motor_setup();
  camera_setup();
}

void loop() {
  if (get_packet(&p)) {
    //error
  }
  if (handle_packet(p)) {
    // error
  }
}

// Executes the actions for a given packet and sends response packet
// Returns 0 on success and >0 on failure
int handle_packet(packet p) {
  struct packet response;
  switch (p.cmd) {
    case SET_MOT_CMD:
      write_thruster(p.value1, translate_motor_val(p.value2));
      break;
    case RD_SENS_CMD:
      break;
    case BLINK_CMD:
//      blink_std();
      break;
    case SET_CAM_CMD:
      int cam_num = p.value1;
      set_camera(cam_num);
      break;
    default:
      break;
  }
  return send_packet(p);
}
