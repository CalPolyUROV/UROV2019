""" Unit testing
"""

# Imports
import serial_coms
import settings
from utils import debug, debug_f
from serial_coms import Packet, make_packet, parse_packet
from task import Task, TaskPriority, TaskType, decode

settings.CHANNELS['test'] = False

# JSON test debug channels
settings.CHANNELS['encode'] = False
settings.CHANNELS['decode'] = False

t1 = Task(TaskType.debug_str, TaskPriority.normal, ["text", 1, 2, "3"])
data = t1.encode()
t2 = decode(data)
assert(t1 == t2)  # json test 1
t3 = decode(b'Garbage data, good luck decoding this')
assert(t3 == None) # json test 2


# Packet test debug channels
settings.CHANNELS['ser_packet'] = False

p1 = Packet(serial_coms.BLINK_CMD, 1, 2, 0b00001111 & (0x80 + 3 + 10))
p2 = parse_packet(b'\x80', b'\x01', b'\x02', b'\x0d')
assert(p1.isValid())  # packet test 1
assert(p2.isValid())  # packet test 2
debug_f('test', "p1: {}", [p1])
debug_f('test', "p2: {}", [p2])
assert(p1 == p2)  # packet test 3

p1 = Packet(serial_coms.EST_CON_CMD, 0, 1, 0)
debug_f('test', "p1: {}", [p1])
assert(not p1.isValid())  # packet test 4
