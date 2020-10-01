from collections import deque
from multiprocessing import Queue as MPQueue
from settings import Settings
from snr.debug import Debugger
from typing import Callable, Tuple
from time import time, sleep
from threading import Thread
from queue import Empty

DAEMON_THREAD = False
SLEEP_TIME = 0.01
JOIN_TIMEOUT = 1


class Timer:
    def __init__(self):
        self.start_time = time()

    def end(self) -> float:
        return time() - self.start_time


class Profiler:
    def __init__(self, debugger: Debugger, settings: Settings):
        if not settings.ENABLE_PROFILING:
            return None
        self.debugger = debugger
        self.time_dict = {}
        self.moving_avg_len = settings.PROFILING_AVG_WINDOW_LEN
        self.q = MPQueue()
        self.terminate_flag = False
        self.consumer_thread = Thread(target=lambda:
                                      self.__consumer(q=self.q,
                                                      action=self.store_task,
                                                      sleep_time=SLEEP_TIME),
                                      daemon=DAEMON_THREAD)
        self.consumer_thread.start()

    def time(self, name: str, handler: Callable):
        time = Timer()
        result = handler()
        self.log_task(name, time.end())
        return result

    def log_task(self, task_type: str, runtime: float):
        self.q.put((task_type, runtime))

    def store_task(self, type_and_runtime: Tuple[str, float]):
        (task_type,  runtime) = type_and_runtime
        self.debugger.debug("profiling_task",
                            "Ran {} task in {:6.3f} us",
                            [task_type, runtime * 1000000])
        # Make sure queue exists
        if self.time_dict.get(task_type) is None:
            self.init_task_type(task_type)
        # Shift elements
        self.time_dict[task_type].append(runtime)
        self.debugger.debug("profiling_avg", "Task {} has average runtime {}",
                            [task_type, self.avg_time(task_type)])

    def init_task_type(self, task_type: str):
        self.time_dict[task_type] = deque(maxlen=self.moving_avg_len)

    def avg_time(self, task_type: str) -> float:
        return self.format_time(sum(self.time_dict[task_type]) /
                                len(self.time_dict[task_type]))

    def dump(self):
        self.debugger.debug(
            "profiling_dump", "Task/Loop type:\t\tAvg runtime: ")
        for k in self.time_dict:
            self.debugger.debug("profiling_dump", "{}:\t\t{}", [
                                k, self.avg_time(k)])

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

    def join(self):
        self.terminate_flag = True
        self.consumer_thread.join(JOIN_TIMEOUT)

    def __consumer(self, q: MPQueue, action: Callable, sleep_time: int):
        """A method to be run by a thread for consuming the contents of a
        queue asynchronously
        """
        # Loop
        while not self.terminate_flag:
            try:
                run = q.get_nowait()
                if run is not None:
                    action(run)
                    run = q.get_nowait()
            except Empty:
                pass
            sleep(sleep_time)

        # Remaining lines
        try:
            run = q.get_nowait()
            while run is not None:
                action(run)
                run = q.get()
        except Exception as e:
            print(f"{e}")
        return
