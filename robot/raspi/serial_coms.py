""" This module manages the serial connection from the robot to the Arduino/Teensy.

TODO: Add more documentation here
"""

# System imports
import serial  # PySerial library

# Our imports
import serial_finder  # Identifies serial ports
import settings
from utils import sleep, debug, exit, attempt
from snr import Task, TaskPriority, TaskType, Relay
from serial_packet import Packet

# encoding scheme
ENCODING = 'ascii'

# Initial value for sequence number
FIRST_SEQNUM = 0

""" List of codes for each command
"""
# TODO: Move list to external file (maybe .txt or .csv),
#       write script to place in Arduino source and python source
#       will not be needed on topside Pi, only on robot
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
        self.serial_port = serial_finder.get_port_to_use()
        
        self.next_seqnum = FIRST_SEQNUM

        def fail_once():
            debug("serial_con", "Failed to open serial port, trying again.")
            sleep(1)  # Wait a second before retrying

        def failure(tries: int):
            if(settings.REQUIRE_SERIAL):
                debug("serial_con", "Could not open serial port after {} attempts. Crashing now.", [
                    tries])
                exit("Could not find port")
            else:
                debug("serial_con", "Giving up on serial connection after {} attempts. Not required in settings.", [
                    tries])
                settings.USE_SERIAL = False

        attempt(self.try_open_serial,
                      settings.SERIAL_MAX_ATTEMPTS,
                      fail_once, failure)

    def try_open_serial(self):
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=settings.SERIAL_BAUD,
                # parity is error checking, odd means the message will have an odd number of 1 bits
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
                timeout=0.1)
            debug('serial_con', "Opened serial connection on {} at baud {}", [
                self.serial_port, settings.SERIAL_BAUD])
            return True
        except serial.serialutil.SerialException:
            return False

    def send_receive_packet(self, p: Packet) -> Packet:
        if(not settings.USE_SERIAL):
            debug(
                "serial", "Serial is not used, ignoring sending of packet {}", [p])
            raise serial.serialutil.SerialException
        # send packet
        self.write_packet(p)
        # Recieve a packet from the Arduino/Teensy
        p = self.read_packet()
        if(p == None):
            debug("serial_con", "Received an empty packet")
        else:
            debug("serial_con", "Received {}", [p])  # Debugging
            return p

    # Send a Packet over serial
    def write_packet(self, p) -> None:
        if(not p.isValid()):
            debug("serial_con", "Ignoring sending of invalid packet {}", [p])
            return
        self.serial_connection.write(p.cmd)
        self.serial_connection.write(p.val1)
        self.serial_connection.write(p.val2)
        self.serial_connection.write(p.seqnum_chksum)
        debug("serial_con", "Sent {}", [p])
        return

    # Read in a packet from serial
    # TODO: ensure that this effectively recieves data over serial
    def read_packet(self) -> Packet or None:
        _cmd = self.serial_connection.read(size=1)
        if (_cmd == b''):
            _cmd = self.serial_connection.read(size=1)
        _val1 = self.serial_connection.read(size=1)
        _val2 = self.serial_connection.read(size=1)
        _seqnum_chksum = self.serial_connection.read(size=1)
        debug('ser_packet', "Received: {}{}{}{}", [
              _cmd, _val1, _val2, _seqnum_chksum])
        # TODO: ensure that chksum is correct
        get_next_seqnum()
        return parse_packet(_cmd, _val1, _val2, _seqnum_chksum)
        # Warning, this will not catch packets with invalid checksums

    # Send the inital packet and wait for the correct response
    def establish_contact(self):
        p_out = Packet.new_packet(
            EST_CON_CMD, EST_CON_VAL1, EST_CON_VAL2, FIRST_SEQNUM)
        debug('serial_con', "Establishing connection by sending {}", [p_out])
        # Send initial packet and receive response
        p_in = self.send_receive_packet(p_out)
        if((p_in.cmd == EST_CON_ACK) &
           (p_in.val1 == EST_CON_VAL1) &
           (p_in.val2 == EST_CON_VAL2)):
            # good
            debug("serial_con", "Sucessfully established contact over serial")
            return []
        else:
            # bad
            debug("serial_con", "Response to initial contact was not satisfactory")
            # TODO: Add logic to retry this a few times
            t = Task(TaskType.serial_est_con, TaskPriority.high, [])
            return [t]

    def new_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets to send (chksum is created)
        """
        seqnum = self.get_next_seqnum()
        chksum = Packet.calc_chksum(cmd, val1, val2, seqnum)
        return Packet(cmd, val1, val2, ((seqnum << 4) + chksum))

    def make_packet(self, cmd: int, val1: int, val2: int, chksum: int):
        """ Constructor for building packets (chksum is given)
        """
        # chksum = calc_chksum(cmd, val1, val2, seqnum)
        return Packet(cmd, val1, val2, ((self.get_next_seqnum() << 4) + chksum))

    def get_next_seqnum(self) -> int:
        self.next_seqnum += 1
        return self.next_seqnum
