""" This module manages the serial connection from the robot to the Arduino/Teensy.

TODO: Add more documentation here
"""
# System imports
import serial  # PySerial library
from sys import exit  # End the program when things fail
from time import sleep  # Wait before retrying sockets connection

# Our imports
import serial_finder  # Identifies serial ports
from debug import debug
from debug import debug_f

# Serial Baudrate, encoding scheme
SERIAL_BAUD = 9600
ENCODING = 'ascii'

# Maximum number of times to try openeing a serial port
MAX_ATTEMPTS: int = 4

# Bitmask for extracting checksums from seqnum_chksum
# Do not use directly, implement a checksum verification method
# TODO: verify checksums, probably in read_packet()
CHKSUM_MASK = 0x0F

# Initial value for sequence number
FIRST_SEQNUM = 0

""" List of codes for each command
"""
# TODO: Move list to external file (maybe .txt or .csv),
#       write script to place in Arduino source and python source
#       will not be needed on topside Pi, only on robot
EST_CON_CMD = 0x00  # cmd of initial packet
EST_CON_ACK = 0x01  # cmd for response to initial packet
SET_MOT_CMD = 0x20  # set motor (call)
SET_MOT_ACK = 0x21  # motor has been set (reponse)
RD_SENS_CMD = 0x40  # request read sensor value
INV_CMD_ACK = 0xFF  # Invalid command, value2 of response contains cmd

# Magic numbers to verify correct initial packet and response
EST_CON_VAL1 = 0b10100101
EST_CON_VAL2 = 0b01011010


class Packet:
    """ Packet class for storing information that is sent and received over serial

    """
    # Internal cosntructor

    def __init__(self, cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        self.cmd = cmd
        self.val1 = val1
        self.val2 = val2
        self.seqnum_chksum = seqnum_chksum

    # Constructor for building packets to send (chksum is created)
    def make_packet(self, cmd: bytes, val1: bytes, val2: bytes, seqnum: bytes):
        return Packet(cmd, val1, val2, (seqnum << 4) + self.calc_chksum(cmd, val1, val2, seqnum))

    # Constructor for building packets that have been received, untrusted checksums
    def read_packet(self, cmd: bytes, val1: bytes, val2: bytes, seqnum_chksum: bytes):
        if(self.calc_chksum(cmd, val1, val2, self.extract_seqnum(seqnum_chksum)) == self.extract_chksum(seqnum_chksum)):
            return Packet(cmd, val1, val2, seqnum_chksum)

    def extract_seqnum(self, seqnum_chksum: bytes) -> bytes:
        return seqnum_chksum >> 4

    def extract_chksum(self, seqnum_chksum: bytes) -> bytes:
        return seqnum_chksum & CHKSUM_MASK

    def calc_chksum(self, cmd, val1, val2, seqnum) -> bytes:
        return (cmd +
                (val1 * 3) +
                (val2 * 5) +
                (seqnum * 7)) & CHKSUM_MASK
        # idk, it has primes
        # TODO: Make this better, but it must match on this and the Arduino/Teensy. (Maybe CRC32?)

    def __repr__(self):
        return """cmd: {}\n
        val1: {}\n
        val2: {}\n
        chksum_seqnum: {}""".format(self.cmd, self.val1, self.val2, self.seqnum_chksum)

#


def find_port():
    """ Finds a serial port for the serial connection

    Calls the serial_finder library to search the operating system for serial ports
    """
    port = None
    attempts: int = 0
    while(port == None):
        try:
                # Get a list of all serial ports
            debug("serial", "Searching for serial ports")
            ports = serial_finder.serial_ports()
            debug("serial", "Found ports:")
            for p in ports:
                debug("serial", p)
            # Select the port
            port = serial_finder.find_port(ports)
            debug_f("serial", "Using port: {}", [port])
            return port

        except serial.serialutil.SerialException:
            pass
        if (attempts > MAX_ATTEMPTS):
            debug_f("serial", "Could not find serial port after {} attempts. Crashing now.", [
                    attempts])
            exit(1)
            attempts += 1
        debug("serial", "Failed to find serial port, trying again.")
        sleep(1)  # Wait a second before retrying


class SerialConnection:
    # Default port arg finds a serial port for the arduino/Teensy
    def __init__(self, serial_port=find_port()):
        attempts: int = 0
        port_open: bool = False
        while(not port_open):
            try:
                self.serial_connection = serial.Serial(
                    port=serial_port,
                    baudrate=SERIAL_BAUD,
                    # parity is error checking, odd means the message will have an odd number of 1 bits
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
                    timeout=0.1)
                port_open = True
            except serial.serialutil.SerialException:
                if (attempts > MAX_ATTEMPTS):
                    debug_f("serial", "Could not open serial port after {} attempts. Crashing now.", [
                            attempts])
                    exit(1)
                attempts += 1
                debug("serial", "Failed to open serial port, trying again.")
                sleep(1)  # Wait a second before retrying

    # Send a Packet over serial
    def write_packet(self, p) -> None:
        # TODO: prevent the sending of invalid packets
        self.serial_connection.write(p.cmd)
        self.serial_connection.write(p.val1)
        self.serial_connection.write(p.val2)
        self.serial_connection.write(p.seqnum_chksum)

    # Read in a packet from serial
    def read_packet(self) -> Packet or None:
        _cmd = self.serial_connection.read(size=1)
        _val1 = self.serial_connection.read(size=1)
        _val2 = self.serial_connection.read(size=1)
        _seqnum_chksum = self.serial_connection.read(size=1)
        return Packet(_cmd, _val1, _val2, _seqnum_chksum)
        # Warning, this will not catch packets with invalid checksums

    def send_receive_packet(self, p: Packet) -> Packet:
        # send packet
        self.write_packet(p)
        # Recieve a packet from the Arduino/Teensy
        p = self.read_packet()
        if(p == None):
            debug("serial", "Received an invalid packet")
        else:
            debug("serial", p)  # Debugging
            return p

    # Send the inital packet and wait for the correct response
    def establish_contact(self):
        # Send initial packet
        p_out = Packet(EST_CON_CMD, EST_CON_VAL1, EST_CON_VAL2, FIRST_SEQNUM)
        # Receive response
        p_in = self.send_receive_packet(p_out)
        # TODO: Verify correctness of initial packet response from Arduino/Teensy
        #       Check arduino source to ensure order of response values, they might get flipped
        if((p_in.cmd == EST_CON_ACK) &
           (p_in.val1 == EST_CON_VAL1) &
           (p_in.val2 == EST_CON_VAL2)):
            # good
            return
        else:
            # bad
            debug("serial", "Response to initial contact was not satisfactory")
            # TODO: Add logic to retry this a few times
            return
