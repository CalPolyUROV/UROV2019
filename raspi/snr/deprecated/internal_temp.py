# import os
# from collections import deque
# from typing import Callable

# import settings
# from snr.async_endpoint import AsyncEndpoint
# from snr.utils import Profiler, debug

# CMD = "vcgencmd measure_temp"
# INVALID_VALUE = -2


# def measure_temp() -> int:
#     """Only usable on Raspi
#     """
#     try:
#         temp = os.popen(CMD).readline()[5: 8]
#         return int(temp)
#     except Exception as error:
#         self.dbg("int_temp_mon", "Error reading temperature: {}",
#               [error.__repr__()])
#         return INVALID_VALUE


# class IntTempMon(AsyncEndpoint):
#     """AsyncEndpoint for internal Raspberry Pi temperature monitoring

#     Settings toggle of this class' use must be done in the calling
#     class because topside and robot toggles for this device are separate
#     """

#     def __init__(self, name: str, store_data: Callable, profiler: Profiler):
#         super().__init__(name,
#                          self.monitor_temp,
#                          settings.INT_TEMP_MON_TICK_RATE,
#                          profiler)
#         self.store_data = store_data
#         self.deque = deque()
#         self.sum = 0.0

#         self.init_temp()
#         self.loop()

#     def init_temp(self):
#         """Prepare the monitor for use"""
#         for i in range(0, settings.INT_TEMP_MON_AVG_PERIOD):
#             self.deque.appendleft(i)
#             self.sum += i

#     def monitor_temp(self):
#         """Main entry point called during loop"""
#         self.queue_reading(measure_temp())
#         avg = self.compute_avg()
#         self.store_data(avg)  # Send data to Node's datastore
#         self.dbg("int_temp_mon", "Temperature: {}'C", [avg])

#     def queue_reading(self, new_val: int):
#         """Place the temperature value in the queue and maintain the sum"""
#         self.sum -= self.deque.pop()
#         self.deque.appendleft(new_val)
#         self.sum += new_val

#     def compute_avg(self) -> float:
#         return self.sum / settings.INT_TEMP_MON_AVG_PERIOD

#     def terminate(self):
#         super().set_terminate_flag()
