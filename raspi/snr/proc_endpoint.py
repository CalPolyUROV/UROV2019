""" SNR framework for scheduling and task management

Node: Task queue driven host for data and endpoints
AsyncEndpoint: Generate and process data for Nodes
Relay: Server data to other nodes
"""
import signal
from time import time
from typing import Callable
from multiprocessing import Process

from snr.endpoint import Endpoint
from snr.node import Node
from snr.utils import debug, print_exit, sleep
from snr.profiler import Timer


class ProcEndpoint(Endpoint):
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
        if parent:
            self.profiler = parent.profiler
        else:
            self.profiler = None

    def set_delay(self, tick_rate_hz: float):
        if tick_rate_hz == 0:
            self.delay = 0.0
        else:
            self.delay = 1.0 / tick_rate_hz

    def start_threaded_loop(self):
        debug("framework", "Starting async endpoint {} thread", [self.name])
        self.proc = Process(target=self.threaded_method(), daemon=True)
        # thread.start_new_thread(self.threaded_method, ())

    def threaded_method(self):
        # signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.setup()
        try:
            while not self.terminate_flag:
                if self.profiler is None:
                    self.loop_handler()
                else:
                    self.profiler.time(self.name, self.loop_handler)

                    # debug("profiling_endpoint",
                    #       "Ran {} task in {:6.3f} us",
                    #       [self.name, runtime * 1000000])

                self.tick()
        except Exception as e:
            if e is KeyboardInterrupt:
                return
            else:
                pass

        debug("framework", "Async endpoint {} exited loop", [self.name])
        # print_exit("Endpoint thread exited by termination")
        return

    def get_name(self):
        return self.name

    def tick(self):
        # TODO: Ensure that this does not block other threads: thread.sleep()?
        if (self.delay == 0.0):
            debug("framework_verbose",
                  "asyncendpoint {} does not sleep (max tick rate)",
                  [self.name])
        else:
            sleep(self.delay)

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating endpoint {}", [self.name])

    def terminate(self):
        raise NotImplementedError
