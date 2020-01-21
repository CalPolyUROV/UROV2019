from collections import deque
from typing import Callable
from time import time

import settings
from snr.utils import debug


class Timer:
    def __init__(self):
        self.start_time = time()

    def end(self) -> float:
        return time() - self.start_time


class Profiler:
    def __init__(self):
        self.time_dict = {}
        self.moving_avg_len = settings.PROFILING_AVG_WINDOW_LEN

    def time(self, name: str, handler: Callable):
        time = Timer()
        result = handler()
        self.log_task(name, time.end())
        return result

    def log_task(self, task_type: str, runtime: float):
        debug("profiling_task",
              "Ran {} task in {:6.3f} us",
              [task_type, runtime * 1000000])
        # Make sure queue exists
        if self.time_dict.get(task_type) is None:
            self.init_task_type(task_type)
        # Shift elements
        self.time_dict[task_type].append(runtime)
        debug("profiling_avg", "Task {} has average runtime {}",
              [task_type, self.avg_time(task_type)])

    def init_task_type(self, task_type: str):
        self.time_dict[task_type] = deque(maxlen=self.moving_avg_len)

    def avg_time(self, task_type: str) -> float:
        return self.format_time(sum(self.time_dict[task_type]) /
                                len(self.time_dict[task_type]))

    def dump(self):
        debug("profiling_dump", "Task/Loop type:\t\tAvg runtime: ")
        for k in self.time_dict:
            debug("profiling_dump", "{}:\t\t{}", [k, self.avg_time(k)])

    def format_time(self, time_s: float) -> str:
        if time_s > 1:
            return "{:6.3f} s".format(time_s)
        if time_s > 0.001:
            return "{:6.3f} ms".format(time_s * 1000)
        if time_s > 0.000001:
            return "{:6.3f} us".format(time_s * 1000000)
        if time_s > 0.000000001:
            return "{:6.3f} ns".format(time_s * 1000000000)
        return "Could not format time"

    def terminate(self):
        self.dump()
