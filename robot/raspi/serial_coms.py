""" This module manages the serial connection
TODO: Add more documentation here
"""

# System imports
import serial  # PySerial library
from serial import SerialException
import struct
from typing import Union, Tuple

# Our imports
import serial_finder  # Identifies serial ports
import settings
from utils import sleep, debug, u_exit, attempt
from snr import Relay
from task import SomeTasks
from serial_packet import Packet, parse_packet, calc_chksum

# encoding scheme
ENCODING = 'ascii'

""" List of codes for each command
"""
# TODO: Move command list to external file (maybe .txt or .csv),
#       write script to generate in Arduino source and python
#       source will not be needed on topside Pi, only on robot
EST_CON_CMD = 0x10  # cmd of initial packet
EST_CON_ACK = 0x11  # cmd for response to initial packet
SET_MOT_CMD = 0x20  # set motor (call)
SET_MOT_ACK = 0x21  # motor has been set (reponse)
RD_SENS_CMD = 0x40  # request read sensor value
BLINK_CMD = 0x80
BLINK_ACK = 0x81
INV_CMD_ACK = 0xFF  # Invalid command, value2 of response contains cmd

# Magic numbers to verify correct initial packet and response
EST_CON_VAL1 = 0b10100101
EST_CON_VAL2 = 0b01011010


class SerialConnection(Relay):
    # Default port arg finds a serial port for the arduino/Teensy
    def __init__(self):
        debug("serial", "Finding serial port")
        serial_finder.get_port_to_use(self.set_port)
        debug("serial", "Selected port {}", [self.serial_port])

        def fail_once():
            debug("serial_con", "Failed to open serial port, trying again.")
            # sleep(1)  # Wait a second before retrying

        def failure(tries: int):
            if(settings.REQUIRE_SERIAL):
                debug("serial_con",
                      "Could not open serial port after {} tries.",
                      [tries])
                u_exit("Could not open serial port")
            else:
                debug("serial_con",
                      "Abort serial connection after {} tries. Not required.",
                      [tries])
                settings.USE_SERIAL = False

        attempt(self.try_open_serial,
                settings.SERIAL_MAX_ATTEMPTS,
                fail_once, failure)

    def set_port(self, port: str):
        debug("serial", "Setting port to {}", [port])
        self.serial_port = port

    def try_open_serial(self):
        sleep(settings.SERIAL_SETUP_WAIT_PRE)
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=settings.SERIAL_BAUD,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=settings.SERIAL_TIMEOUT)
            # Connection should be opened by constructor
            # self.serial_connection.open()
            if self.serial_connection.is_open:
                debug('serial_con',
                      "Opened serial connection on {} at baud {}",
                      [self.serial_port, settings.SERIAL_BAUD])
                sleep(settings.SERIAL_SETUP_WAIT_POST)
                while self.serial_connection.in_waiting > 0:
                    self.serial_connection.read()
                return True
            return False
        except serial.serialutil.SerialException as error:
            debug("serial_con", "Error opening port: {}", [error.__repr__()])
            return False

    # Send and receive data over serial
    def send_receive(self, cmd_type: str, data: list) -> SomeTasks:
        t = []
        if not settings.USE_SERIAL:
            debug("serial",
                  "Serial is not used, ignoring sending of data {}", [data])
            return None

        if cmd_type.__eq__("blink"):
            p = self.new_packet(BLINK_CMD, data[0], data[1])
            self.send_receive_packet(p)
        elif cmd_type.__eq__("set_motor"):
            (direction, throttle) = self.translate_motor(
                data[0], data[1])
            p = self.new_packet(SET_MOT_CMD, direction, throttle)
            self.send_receive_packet(p)
        elif cmd_type.__eq__("read_sensor"):
            pass
        else:
            debug("serial", "Type of serial command {} not recognized",
                  [cmd_type])
            return None
        return t

    # Send and receive a serial packet
    def send_receive_packet(self, p: Packet) -> Packet:
        if(not settings.USE_SERIAL):
            debug("serial",
                  "Serial is not used, ignoring sending of packet {}", [p])
            raise serial.serialutil.SerialException
        # send packet
        self.write_packet(p)
        # Recieve a packet from the Arduino/Teensy
        p_recv = self.read_packet()
        if p_recv is None:
            debug("serial_con", "Received an empty packet")
        elif p.weak_eq(p_recv):
            debug("serial_con", "Received echo packet")
        else:
            debug("serial_con", "Received {}", [p_recv])  # Debugging
        return p

    # Send a Packet over serial

    def write_packet(self, p):
        if not p.isValid():
            debug("serial_con", "Ignoring sending of invalid packet {}", [p])
            return
        if not self.serial_connection.is_open:
            debug("serial_con", "Aborting send, Serial is not open: {}",
                  [self.serial_connection])
            return
        # debug("serial_con", "{}", [self.serial_connection])
        packed_format = "BBBB"
        data_bytes = struct.pack(packed_format, p.cmd, p.val1, p.val2, 0)
        expected_size = struct.calcsize(packed_format)
        # byte_format = "B"
        # cmd_byte = struct.pack(byte_format, p.cmd)
        # val1_byte = struct.pack(byte_format, p.val1)
        # val2_byte = struct.pack(byte_format, p.val2)
        # zero_byte = struct.pack(byte_format, 0)
        # expected_size = struct.calcsize(byte_format) * 4
        debug("serial_con", "Trying to send packet of expected size {}",
              [expected_size])
        sent_bytes = 0
        try:
            sent_bytes += self.serial_connection.write(data_bytes)

            # sent_bytes += self.serial_connection.write(cmd_byte)
            # # sleep(0.5)
            # sent_bytes += self.serial_connection.write(val1_byte)
            # # sleep(0.5)
            # sent_bytes += self.serial_connection.write(val2_byte)
            # # sleep(0.5)
            # sent_bytes += self.serial_connection.write(zero_byte)
            debug("serial_con", "Out-waiting: {}",
                  [self.serial_connection.out_waiting])
            # sleep(0.5)
            # self.serial_connection.flush()
            # sleep(0.5)
        except serial.serialutil.SerialException as error:
            debug("serial_con", "Error sending packet: {}", [error.__repr__()])
            return
        # debug("serial_con",
        #       "{} bytes sent: {}{}{}{}",
        #       [sent_bytes, cmd_byte, val1_byte, val2_byte, zero_byte])

        debug("serial_con", "Sent {}", [p])
        return

    # Read in a packet from serial
    # TODO: ensure that this effectively recieves data over serial
    def read_packet(self) -> Union[Packet, None]:
        if not self.serial_connection.is_open:
            debug("serial_con", "Aborting read, Serial is not open: {}",
                  [self.serial_connection])
            return None

        # debug("serial_con", "{}", [self.serial_connection])
        debug("serial_verbose", "Waiting for bytes, {} ready", [
              self.serial_connection.in_waiting])
        tries = 0
        while self.serial_connection.in_waiting < 3:
            # self.serial_connection.write(b'\0x00')
            tries = tries + 1
            # debug("serial_verbose", "waiting... {} of 4",
            #       [self.serial_connection.in_waiting])
            # if tries > settings.SERIAL_MAX_ATTEMPTS:
            #     debug("serial_con", "No reponse from device")
            #     return None
            # sleep(0.5)
        debug("serial_verbose", "Received enough bytes after {} tries", [tries])
        debug("serial_verbose", "Reading, {} bytes ready",
              [self.serial_connection.in_waiting])
        try:
            recv_bytes = self.serial_connection.read(size=4)
        except Exception as error:
            debug("serial_receive", "Error reading serial: {}",
                  [error.__repr__()])
        debug("serial_verbose", "Read bytes from serial")
        debug("serial_verbose", "type(recv_bytes) = {}", [type(recv_bytes)])
        _cmd = recv_bytes[0]
        _val1 = recv_bytes[1]
        _val2 = recv_bytes[2]
        _chksum = recv_bytes[3]
        debug('serial_con', "Unpacked: cmd: {}.{}, val1: {}.{}, val2: {}.{}",
          [_cmd, _cmd.__class__, _val1, _val1.__class__, _val2, _val2.__class__])
        # TODO: ensure that chksum is correct
        # p = parse_packet(_cmd, _val1, _val2, _chksum)
        p = Packet(_cmd, _val1, _val2, _chksum)
        if p.isValid():
            return p
        debug("ser_packet", "Whoa! Read invalid packet {}", [p])
        return p

    motor_translate_dict = {"x": 0,
                            "y": 1,
                            "z": 2,
                            "yaw": 3,
                            "pitch": 4,
                            "roll": 5}

    def map_thrust_value(self, speed: int) -> int:
        return int ((speed + 100) * 1.275)

    def translate_motor(self, motor_str: str, speed: int) -> Tuple[int, int]:
        mapped_speed = self.map_thrust_value(speed)
        motor_int = SerialConnection.motor_translate_dict[motor_str]
        return (motor_int, mapped_speed)

    def new_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets to send (chksum is created)
        """
        debug("ser_packet",
              "Preparing packet: cmd: {}, val1: {}, val2: {}",
              [cmd, val1, val2])
        # debug("ser_packet", "Prepared packet: cmd: {}, val1: {}, val2: {}", [
        #   cmd, val1, val2])
        chksum = calc_chksum(cmd, val1, val2)

        return Packet(cmd, val1, val2, chksum)

    def make_packet(self, cmd: int, val1: int, val2: int, chksum: int):
        """ Constructor for building packets (chksum is given)
        """
        # chksum = calc_chksum(cmd, val1, val2)
        return Packet(cmd, val1, val2, chksum)

    def terminate(self):
        debug("serial_con", "Closing serial connection")
        settings.USE_SERIAL = False
        # self.serial_connection.flush()
        self.serial_connection.close()
        debug("serial_con", "Closed serial connection")
