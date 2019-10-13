""" SNR framework for scheduling and task management

Node: Task queue driven host for data and endpoints
AsyncEndpoint: Generate and process data for Nodes
Relay: Server data to other nodes
"""

from collections import deque
from time import time
from typing import Callable, Union

import _thread as thread
import settings
from snr.datastore import Datastore
from snr.task import TaskHandler, SomeTasks, Task, TaskPriority, TaskSource
from snr.utils import Profiler, debug, sleep, print_exit
from snr.endpoint import Endpoint


class AsyncEndpoint(Endpoint):
    """An Asynchronous endpoint of data for a node

    An AsyncEndpoint is part of a node, and runs in its own thread. An
    endpoint may produce data to be stored in the Node or retreive data from
    the Node. The endpoint has its loop handler function run according to its
    tick_rate (Hz).
    """

    def __init__(self, name: str, loop_handler: Callable,
                 tick_rate: float, profiler: Profiler):
        self.name = name
        self.loop_handler = loop_handler
        self.terminate_flag = False
        self.set_delay(tick_rate)
        self.profiler = profiler

    def set_delay(self, tick_rate: float):
        if tick_rate == 0:
            self.delay = 0.0
        else:
            self.delay = 1.0 / tick_rate

    def loop(self):
        debug("framework", "Starting async endpoint {} thread", [self.name])
        thread.start_new_thread(self.threaded_loop, ())

    def threaded_loop(self):
        while not self.terminate_flag:
            if self.profiler is None:
                self.loop_handler()
            else:
                start_time = time()
                self.loop_handler()
                runtime = time() - start_time
                self.profiler.log_task(self.name, runtime)
                debug("profiling_endpoint", "Ran {} task in {:6.3f} us",
                      [self.name, runtime * 1000000])

            self.tick()
        debug("framework", "Async endpoint {} exited loop", [self.name])
        print_exit("Endpoint thread exited by termination")

    def get_name(self):
        return self.name

    def tick(self):
        sleep(self.delay)
        # TODO: Ensure that this does not block other threads

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating endpoint {}", [self.name])

    def terminate(self):
        """Execute actions needed to destruct a AsyncEndpoint
        """
        raise NotImplementedError(
            "Subclass of endpoint does not implement terminate()")
