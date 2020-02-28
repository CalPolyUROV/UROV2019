""" SNR framework for scheduling and task management

Node: Task queue driven host for data and endpoints
AsyncEndpoint: Generate and process data for Nodes
Relay: Server data to other nodes
"""

from time import time
from typing import Callable

import _thread
# from threading import Thread
# TODO: Move to non-deprecated threads
from snr.endpoint import Endpoint
from snr.node import Node
from snr.utils.utils import sleep
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
        super().__init__(parent, name)
        self.setup = setup_handler
        self.loop_handler = loop_handler
        self.terminate_flag = False
        self.set_delay(tick_rate_hz)

        if parent:
            self.profiler = parent.profiler
        else:
            self.profiler = None

    def set_delay(self, tick_rate_hz: float):
        if tick_rate_hz == 0:
            self.delay = 0.0
        else:
            self.delay = 1.0 / tick_rate_hz

    def start_loop(self):
        self.dbg("framework",
                 "Starting async endpoint {} thread",
                 [self.name])
        _thread.start_new_thread(self.threaded_method, ())
        # self.thread = Thread(target=self.threaded_method,
        #                      args=None)
        # self.thread.start()

    def join(self):
        """Externaly wait to shutdown a threaded endpoint
        """
        self.set_terminate_flag("join")

    def threaded_method(self):
        self.setup()

        while not self.terminate_flag:
            if self.profiler is None:
                self.loop_handler()
            else:
                self.profiler.time(self.name, self.loop_handler)

                # self.dbg("profiling_endpoint",
                #       "Ran {} task in {:6.3f} us",
                #       [self.name, runtime * 1000000])

            self.tick()

        self.dbg("framework", "Async endpoint {} exited loop", [self.name])
        self.terminate()
        # print_exit("Endpoint thread exited by termination")

    def get_name(self):
        return self.name

    def tick(self):
        # TODO: Ensure that this does not block other threads: thread.sleep()?
        if (self.delay == 0.0):
            self.dbg("framework_warning",
                     "async_endpoint {} does not sleep (max tick rate)",
                     [self.name])
        else:
            sleep(self.delay)

    def set_terminate_flag(self, reason: str):
        self.terminate_flag = True
        self.dbg("framework",
                 "Preparing to terminating async_endpoint {} for {}",
                 [self.name, reason])
