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
from snr.utils.utils import sleep
from snr.profiler import Timer

JOIN_TIMEOUT = 0.5


class ProcEndpoint(Endpoint):
    """An Asynchronous (Thread) endpoint for a node

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
        self.dbg("framework", "Starting proc endpoint {} process", [self.name])
        self.proc = self.get_proc()
        self.proc.start()

    def get_proc(self):
        return Process(target=self.threaded_method, daemon=True)

    def join(self):
        self.set_terminate_flag("join")
        self.proc.join(JOIN_TIMEOUT)

    def threaded_method(self):
        # signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
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
        except (Exception, KeyboardInterrupt) as e:
            self.dbg("proc_endpoint_error", "{}, e: {}", [self.name, str(e)])
            # self.parent.set_terminate_flag(str(e))

        self.dbg("proc_endpoint_event",
                 "Proc endpoint {} exited loop",
                 [self.name])
        self.terminate()
        return

    def get_name(self):
        return self.name

    def tick(self):
        if (self.delay == 0.0):
            self.dbg("framework_warning",
                     "proc_endpoint {} does not sleep (max tick rate)",
                     [self.name])
        else:
            sleep(self.delay)

    def set_terminate_flag(self, reason: str):
        self.terminate_flag = True
        self.dbg("framework",
                 "Preparing to terminate proc_endpoint {} for {}",
                 [self.name, reason])

    def terminate(self):
        raise NotImplementedError
