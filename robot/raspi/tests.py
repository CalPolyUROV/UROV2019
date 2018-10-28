from task import Task
from task import TaskType
from task import TaskPriority
from task import decode
import serial_coms
from serial_coms import Packet
from serial_coms import make_packet
from serial_coms import parse_packet

t1 = Task(TaskType.debug_str, TaskPriority.normal, ["text", 1, 2, "3"])
data = t1.encode()
t2 = decode(data)

assert(t1 == t2)

p1 = Packet(serial_coms.BLINK_CMD, 1, 2, 0b00001111 & (0x80 + 3 + 10))
p2 = parse_packet(b'\x80', b'\x01', b'\x02', b'\x00')

print("p1: {}".format(p1))
print("p2: {}".format(p2))
assert(p1 == p2)

