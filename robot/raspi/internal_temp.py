import os
import _thread
from collections import deque
from typing import Callable

import settings
from utils import sleep, debug
from snr import Source
from datastore import Datastore

CMD = "vcgencmd measure_temp"
ARRAY_SIZE = 4
INVALID_VALUE = -2


def measure_temp() -> int:
    """Only usable on Raspi
    """
    try:
        temp = os.popen(CMD).readline()[5: 8]
        return int(temp)
    except Exception as error:
        debug("int_temp_mon", "Error reading temperature: {}",
              [error.__repr__()])
        return INVALID_VALUE


class IntTempMon(Source):
    """Threaded Source class for internal Raspberry Pi temperature monitoring

    Settings toggle of this class' use must be done in the calling class 
    because topside and robot toggles for this device are separate
    """

    def __init__(self, name: str, store_data: Callable):
        super().__init__(name, self.monitor_temp, settings.INT_TEMP_MON_TICK_RATE)
        self.store_data = store_data
        self.deque = deque(-1 for i in range(0, ARRAY_SIZE))

        self.init_temp()
        self.loop()

    def init_temp(self):
        for i in range(0, ARRAY_SIZE):
            self.queue_reading(measure_temp())

    def monitor_temp(self):
        self.queue_reading(measure_temp())
        avg = self.compute_avg()
        self.store_data(self.name, avg)
        debug("int_temp_mon", "Temperature: {}'C", [avg])

    def queue_reading(self, new_val: int):
        self.deque.pop()
        self.deque.appendleft(new_val)

    def compute_avg(self) -> int:
        sum = 0
        for i in self.deque:
            if i is not None:
                sum += i
        return sum / ARRAY_SIZE

    def terminate(self):
        super().set_terminate_flag()
