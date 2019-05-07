
//#include <TeensyThreads.h>

#include "settings.h"
#include "defs.h"
#include "serial.h"
#include "packet.h"
#include "blink.h"
#include "motors.h"
#include "cameras.h"

// Sequence number keeps track of packet order
// Do not directly access or modify the global sequence number
// Always use the inc_seqnum() and get_seqnum_nibble() functions

packet p;
//int motor_input = MOTOR_INPUT_CENTER;
//int motor_input_delta = 5;

void setup() {
  //  initialize_serial();
  Serial.begin(COMS_BAUD);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }

  blink_setup();
  blink_std();

  //  seqnum = FIRST_SEQNUM;
  //establishContact();  // send a byte to establish contact until receiver responds
  led_on();
  motor_setup();
  camera_setup();
  led_off();
}

void loop() {
  if (get_packet(&p)) {
    //error
  }
  if (handle_packet(p)) {
    // error
  }

  //  if (motor_input > MOTOR_INPUT_MAX || motor_input < MOTOR_INPUT_MIN) {
  //    motor_input_delta = -1 * motor_input_delta;
  //    delay(2000);
  //  }
  //  for (int i = 0; i < NUM_MOTORS; i++) {
  //    set_motor_target(i, motor_input);
  //  }

  update_all_motors_speeds();
  //  motor_input += motor_input_delta;
  //  delay(MOTOR_DELTA_MS);
}

// Executes the actions for a given packet and sends response packet
// Returns 0 on success and >0 on failure
int handle_packet(packet p) {
  struct packet response;
  switch (p.cmd) {
    case SET_MOT_CMD:

      int axis_index = p.value1;
      set_axis(axis_index, p.value2 - COMS_CENTER);
      trigger_motor_updates(axis_index);
      break;
    case RD_SENS_CMD:
      break;
    case BLINK_CMD:
      blink_std();
      break;
    case SET_CAM_CMD:
      set_camera(p.value1);
      break;
    default:
      break;
  }
  response = p;
  int result = send_packet(response);
  return result;
}

//
//// function for prepping a response to an invalid packet, for when you want to say "NOPE"
//void create_inv_packet(packet *response, packet p, byte seqnum_nibble) {
//  //debug_packet(p);
//  create_packet(response, INV_CMD_ACK, p.value1, p.cmd, seqnum_nibble);
//}


// check for correct check sum
//  if (extract_chksum(seqnum_chksum_byte) != extract_chksum(p->seqnum_chksum)) {
//
//    // checksum failed
//    // debug print result
//    return 1;
//  }
// Check squence number after checksum because seqnum of mangled packet is useless
//  if (extract_seqnum(p->seqnum_chksum) != expect_seqnum_nibble) {
//    // incorrect seqnum
//    // debug print result
//    return 2;
//  }
// Success
//  return 0;
//}
