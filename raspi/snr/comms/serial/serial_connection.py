""" This module manages the serial connection
between the Pi and microcontroller
TODO: Add more documentation here
"""

from typing import Union

import serial

import settings
import snr.comms.serial.serial_finder
from snr.comms.serial.packet import (BLINK_CMD, PACKET_SIZE, SET_CAM_CMD,
                                     SET_MOT_CMD, Packet)
from snr.endpoint import Endpoint
from snr.node import Node
from snr.task import SomeTasks, Task, TaskType
from snr.utils import attempt, debug, print_exit, sleep


class SerialConnection(Endpoint):
    # Default port arg finds a serial port for the arduino/Teensy
    def __init__(self, parent: Node,
                 input: str, output: str):
        super().__init__(parent)
        if settings.SIMULATE_SERIAL:
            self.serial_connection = None
            self.simulated_bytes = None
            return

        debug("serial_verbose", "Finding serial port")
        serial_finder.get_port_to_use(self.set_port)
        debug("serial", "Selected port {}", [self.serial_port])

        def fail_once():
            debug("serial_warning",
                  "Failed to open serial port, trying again.")

        def failure(tries: int):
            debug("serial_error",
                  "Could not open serial port after {} tries.",
                  [tries])
            print_exit("Could not open serial port")

        attempt(self.try_open_serial,
                settings.SERIAL_MAX_ATTEMPTS,
                fail_once, failure)

    def get_new_tasks(self):
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        sched_list = []
        if t.task_type == TaskType.serial_com:
            debug("serial_verbose",
                  "Executing serial com task: {}", [t.val_list])
            result = self.serial_connection.send_receive(t.val_list[0],
                                                         t.val_list[1::])
            if result is None:
                debug("robot",
                      "Received no data in response from serial message")
            elif isinstance(result, Task):
                sched_list.append(result)
            elif isinstance(result, list):
                for new_task in list(result):
                    sched_list.append(new_task)

        # Blink test
        elif t.task_type == TaskType.blink_test:
            self.serial_connection.send_receive("blink", t.val_list)
        return sched_list

    def set_port(self, port: str):
        debug("serial", "Setting port to {}", [port])
        self.serial_port = port

    def try_open_serial(self):
        if settings.SIMULATE_SERIAL:
            debug("serial_sim",
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
                debug('serial',
                      "Opened serial connection on {} at baud {}",
                      [self.serial_port, settings.SERIAL_BAUD])
                sleep(settings.SERIAL_SETUP_WAIT_POST)
                while self.serial_connection.in_waiting > 0:
                    self.serial_connection.read()
                return True
            return False
        except Exception as error:
            debug("serial_con", "Error opening port: {}", [error.__repr__()])
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
            debug("serial_error", "Type of serial command {} not recognized",
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
            debug("serial_verbose", "Received an empty packet")
        elif p.weak_eq(p_recv):
            debug("serial_verbose", "Received echo packet")
        else:
            debug("serial_verbose", "Received {}", [p_recv])  # Debugging
        return p

    # Send a Packet over serial

    def write_packet(self, p):
        data_bytes, expected_size = p.pack()
        debug("serial_verbose", "Trying to send packet of expected size {}",
              [expected_size])
        sent_bytes = 0

        if settings.SIMULATE_SERIAL:
            debug("serial_sim", "Sending bytes {}", [
                  data_bytes])
            self.simulated_bytes = data_bytes
            return

        try:
            if not self.serial_connection.is_open:
                debug("serial_error", "Aborting send, Serial is not open: {}",
                      [self.serial_connection])
                return
            sent_bytes += self.serial_connection.write(data_bytes)
            debug("serial_verbose", "Sent {} bytes: {}",
                  [sent_bytes, data_bytes])
            debug("serial_verbose", "Out-waiting: {}",
                  [self.serial_connection.out_waiting])
        except serial.serialutil.SerialException as error:
            debug("serial_error", "Error sending packet: {}",
                  [error.__repr__()])
            return
        debug("serial_verbose", "Sent {}", [p])
        return

    # Read in a packet from serial
    # TODO: ensure that this effectively recieves data over serial
    def read_packet(self) -> Union[Packet, None]:
        if settings.SIMULATE_SERIAL:
            debug("serial_sim", "Receiving packet of simulated bytes")
            recv_bytes = self.simulated_bytes
        else:
            if not self.serial_connection.is_open:
                debug("serial_error", "Aborting read, Serial is not open: {}",
                      [self.serial_connection])
                return None

            debug("serial_verbose", "Waiting for bytes, {} ready", [
                self.serial_connection.in_waiting])
            tries = 0
            while self.serial_connection.in_waiting < PACKET_SIZE:
                tries = tries + 1
            debug("serial_verbose",
                  "Received enough bytes after {} tries", [tries])
            debug("serial_verbose", "Reading, {} bytes ready",
                  [self.serial_connection.in_waiting])
            try:
                recv_bytes = self.serial_connection.read(size=PACKET_SIZE)
            except Exception as error:
                debug("serial_receive", "Error reading serial: {}",
                      [error.__repr__()])
        debug("serial_verbose", "Read bytes from serial")
        debug("serial_verbose", "type(recv_bytes) = {}", [type(recv_bytes)])
        cmd = recv_bytes[0]
        val1 = recv_bytes[1]
        val2 = recv_bytes[2]
        s = "Unpacked: cmd: {}.{}, val1: {}.{}, val2: {}.{}"
        debug('serial_verbose', s,
              [cmd, cmd.__class__, val1, val1.__class__, val2, val2.__class__])
        p = Packet(cmd, val1, val2)
        return p

    def map_thrust_value(self, speed: int) -> int:
        if speed > 100:
            return 255
        if speed < -100:
            return 0
        val = int((speed * 1.275) + 127)
        debug("serial_packet",
              "Converted motor speed from {} to {}", [speed, val])
        return val

    def generate_motor_packet(self, motor: int, speed: int) -> Packet:
        mapped_speed = self.map_thrust_value(speed)
        return self.new_packet(SET_MOT_CMD, motor, mapped_speed)

    def new_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets to send (chksum is created)
        """
        debug("serial_verbose",
              "Preparing packet: cmd: {}, val1: {}, val2: {}",
              [cmd, val1, val2])

        return Packet(cmd, val1, val2)

    def make_packet(self, cmd: int, val1: int, val2: int):
        """ Constructor for building packets (chksum is given)
        """
        return Packet(cmd, val1, val2)

    def terminate(self):
        if self.serial_connection is not None:
            debug("serial", "Closing serial connection")
            self.serial_connection.close()
            self.serial_connection = None
        debug("serial", "Closed serial connection")
