""" SNR framework for scheduling and task management

Node: Task queue driven host for data and endpoints
AsyncEndpoint: Generate and process data for Nodes
Relay: Server data to other nodes
"""

from time import time
from typing import Callable

import _thread as thread
from snr.endpoint import Endpoint
from snr.node import Node
from snr.utils import debug, print_exit, sleep
from snr.profiler import Timer


class AsyncEndpoint(Endpoint):
    """An Asynchronous endpoint of data for a node

    An AsyncEndpoint is part of a node, and runs in its own thread. An
    endpoint may produce data to be stored in the Node or retreive data from
    the Node. The endpoint has its loop handler function run according to its
    tick_rate (Hz).
    """

    def __init__(self, parent: Node, name: str,
                 setup_handler: Callable, loop_handler: Callable,
                 tick_rate_hz: float):
        self.parent = parent
        self.name = name
        self.setup = setup_handler
        self.loop_handler = loop_handler
        self.terminate_flag = False
        self.set_delay(tick_rate_hz)
        self.profiler = parent.profiler

    def set_delay(self, tick_rate_hz: float):
        if tick_rate_hz == 0:
            self.delay = 20
        else:
            self.delay = 1.0 / tick_rate_hz

    def start_threaded_loop(self):
        debug("framework", "Starting async endpoint {} thread", [self.name])
        thread.start_new_thread(self.threaded_method, ())

    def threaded_method(self):
        self.setup()

        while not self.terminate_flag:
            if self.profiler is None:
                self.loop_handler()
            else:
                time = Timer()
                self.loop_handler()
                self.profiler.log_task(self.name, time.end())
                # debug(
                #     "profiling_endpoint",
                #     "Ran {} task in {:6.3f} us",
                #     [self.name, runtime * 1000000],
                # )
            self.tick()

        debug("framework", "Async endpoint {} exited loop", [self.name])
        print_exit("Endpoint thread exited by termination")

    def get_name(self):
        return self.name

    def tick(self):
        # TODO: Ensure that this does not block other threads: thread.sleep()?
        sleep(self.delay)

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating endpoint {}", [self.name])

    def terminate(self):
        raise NotImplementedError
