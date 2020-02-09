""" This module manages the serial connection
between the Pi and microcontroller
TODO: Add more documentation here
"""

from typing import Union

import serial

import settings
from snr.comms.serial.serial_finder import *
from snr.comms.serial.packet import (BLINK_CMD, PACKET_SIZE, SET_CAM_CMD,
                                     SET_MOT_CMD, Packet)
from snr.endpoint import Endpoint
from snr.node import Node
from snr.task import SomeTasks, Task
from snr.utils.utils import attempt, print_exit, sleep


class SerialConnection(Endpoint):
    # Default port arg finds a serial port for the arduino/Teensy
    def __init__(self, parent: Node, name: str,
                 input: str, output: str):
        self.task_producers = []
        self.task_handlers = {
            "serial_com": self.handle_serial_com,
            "blink_test": self.handle_blink_test
        }
        super().__init__(parent, name)

        if settings.SIMULATE_SERIAL:
            self.serial_connection = None
            self.simulated_bytes = None
            return

        self.dbg("serial_verbose", "Finding serial port")
        get_port_to_use(self.set_port)
        self.dbg("serial", "Selected port {}", [self.serial_port])

        self.attempt_connect()

    def attempt_connect(self):
        def fail_once():
            self.dbg("serial_warning",
                     "Failed to open serial port, trying again.")

        def failure(tries: int):
            self.dbg("serial_error",
                     "Could not open serial port after {} tries.",
                     [tries])
            print_exit("Could not open serial port")

        attempt(self.try_open_serial,
                settings.SERIAL_MAX_ATTEMPTS,
                fail_once, failure)

    def handle_serial_com(self, t: Task):
        self.dbg("serial_verbose",
                 "Executing serial com task: {}", [t.val_list])
        result = self.send_receive(t.val_list[0],
                                   t.val_list[1::])
        if result is None:
            self.dbg("robot",
                     "Received no data in response from serial message")
        elif isinstance(result, Task):
            sched_list.append(result)
        elif isinstance(result, list):
            for new_task in list(result):
                sched_list.append(new_task)

    def handle_blink_test(self, t: Task):
        self.serial_connection.send_receive("blink",
                                            t.val_list)

    def set_port(self, port: str):
        self.dbg("serial", "Setting port to {}", [port])
        self.serial_port = port

    def try_open_serial(self):
        if settings.SIMULATE_SERIAL:
            self.dbg("serial_sim",
                     "Not opening port", [])
            return None
        sleep(settings.SERIAL_SETUP_WAIT_PRE)
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=settings.SERIAL_BAUD,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=settings.SERIAL_TIMEOUT)
            if self.serial_connection.is_open:
                self.dbg('serial',
                         "Opened serial connection on {} at baud {}",
                         [self.serial_port, settings.SERIAL_BAUD])
                sleep(settings.SERIAL_SETUP_WAIT_POST)
                while self.serial_connection.in_waiting > 0:
                    if self.serial_connection.in_waiting > PACKET_SIZE:
                        self.dbg("serial_warning",
                                 "Extra inbound bytes on serial: {}",
                                 [self.serial_connection.in_waiting])
                    self.serial_connection.read()
                return True
            return False
        except Exception as error:
            self.dbg("serial_con", "Error opening port: {}",
                     [error.__repr__()])
            return False

    # Send and receive data over serial
    def send_receive(self, cmd_type: str, data: list) -> SomeTasks:
        t = []

        if cmd_type.__eq__("blink"):
            p = self.new_packet(BLINK_CMD, data[0], data[1])

            self.send_receive_packet(p)
        elif cmd_type.__eq__("set_motor"):
            p = self.generate_motor_packet(data[0], data[1])

            self.send_receive_packet(p)
        elif cmd_type.__eq__("set_cam"):
            p = self.new_packet(SET_CAM_CMD, data[0], 0)
            self.send_receive_packet(p)
        elif cmd_type.__eq__("read_sensor"):
            pass
        else:
            self.dbg("serial_error", "Type of serial command {} not recognized",
                     [cmd_type])
            return None
        return t

    # Send and receive a serial packet
    def send_receive_packet(self, p: Packet) -> Packet:
        # send packet
        self.write_packet(p)
        # Recieve a packet from the Arduino/Teensy
        p_recv = self.read_packet()
        if p_recv is None:
            self.dbg("serial_verbose", "Received an empty packet")
        elif p.weak_eq(p_recv):
            self.dbg("serial_verbose", "Received echo packet")
        else:
            self.dbg("serial_verbose", "Received {}", [p_recv])  # Debugging
        return p

    # Send a Packet over serial

    def write_packet(self, p):
        data_bytes, expected_size = p.pack()
        self.dbg("serial_verbose", "Trying to send packet of expected size {}",
                 [expected_size])
        sent_bytes = 0

        if settings.SIMULATE_SERIAL:
            self.dbg("serial_sim", "Sending bytes {}", [
                data_bytes])
            self.simulated_bytes = data_bytes
            return

        try:
            if not self.serial_connection.is_open:
                self.dbg("serial_error", "Aborting send, Serial is not open: {}",
                         [self.serial_connection])
                return
            sent_bytes += self.serial_connection.write(data_bytes)
            self.dbg("serial_verbose", "Sent {} bytes: {}",
                     [sent_bytes, data_bytes])
            self.dbg("serial_verbose", "Out-waiting: {}",
                     [self.serial_connection.out_waiting])
        except serial.serialutil.SerialException as error:
            self.dbg("serial_error", "Error sending packet: {}",
                     [error.__repr__()])
            return
        self.dbg("serial_verbose", "Sent {}", [p])
        return

    # Read in a packet from serial
    # TODO: ensure that this effectively recieves data over serial
    def read_packet(self) -> Union[Packet, None]:
        if settings.SIMULATE_SERIAL:
            self.dbg("serial_sim", "Receiving packet of simulated bytes")
            recv_bytes = self.simulated_bytes
        else:
            if not self.serial_connection.is_open:
                self.dbg("serial_error", "Aborting read, Serial is not open: {}",
                         [self.serial_connection])
                return None

            self.dbg("serial_verbose", "Waiting for bytes, {} ready", [
                self.serial_connection.in_waiting])
            tries = 0
            while self.serial_connection.in_waiting < PACKET_SIZE:
                tries = tries + 1
            self.dbg("serial_verbose",
                     "Received enough bytes after {} tries", [tries])
            self.dbg("serial_verbose", "Reading, {} bytes ready",
                     [self.serial_connection.in_waiting])
            try:
                recv_bytes = self.serial_connection.read(size=PACKET_SIZE)
            except Exception as error:
                self.dbg("serial_receive", "Error reading serial: {}",
                         [error.__repr__()])
        self.dbg("serial_verbose", "Read bytes from serial")
        self.dbg("serial_verbose", "type(recv_bytes) = {}", [type(recv_bytes)])
        cmd = recv_bytes[0]
        val1 = recv_bytes[1]
        val2 = recv_bytes[2]
        s = "Unpacked: cmd: {}.{}, val1: {}.{}, val2: {}.{}"
        self.dbg('serial_verbose', s,
                 [cmd, cmd.__class__, val1, val1.__class__, val2, val2.__class__])
        p = Packet(cmd, val1, val2)
        return p

    def map_thrust_value(self, speed: int) -> int:
        if speed > 100:
            return 255
        if speed < -100:
            return 0
        val = int((speed * 1.275) + 127)
        self.dbg("serial_packet",
                 "Converted motor speed from {} to {}", [speed, val])
        return val

    def generate_motor_packet(self, motor: int, speed: int) -> Packet:
        mapped_speed = self.map_thrust_value(speed)
        return self.new_packet(SET_MOT_CMD, motor, mapped_speed)

    def new_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets to send (chksum is created)
        """
        self.dbg("serial_verbose",
                 "Preparing packet: cmd: {}, val1: {}, val2: {}",
                 [cmd, val1, val2])

        return Packet(cmd, val1, val2)

    def make_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets (chksum is given)
        """
        return Packet(cmd, val1, val2)

    def terminate(self):
        if self.serial_connection is not None:
            self.dbg("serial", "Closing serial connection")
            self.serial_connection.close()
            self.serial_connection = None
        self.dbg("serial", "Closed serial connection")
