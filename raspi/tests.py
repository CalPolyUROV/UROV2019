""" Unit testing
"""

import settings
import snr.comms.serial.serial_coms
from snr.comms.serial.packet import Packet
from snr.controller import simulate_input
from snr.task import Task, TaskPriority
from snr.utils import debug

settings.DEBUG_CHANNELS["test"] = False

print(simulate_input())
