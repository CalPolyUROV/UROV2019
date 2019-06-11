"""Various helper utilities used throughout the code
Attempts to document propper usage of such functions
"""

import os
import sys
import time
from collections import deque
from typing import Any, Callable, List, Union

import settings
from snr_task import TaskType


def print_usage() -> None:
    """Prints a Unix style uasge message on how to start the program
    """
    print("usage: python3 main.py (robot | topside)")


def u_exit(reason: str) -> None:
    """Kills the program after printing the supplied str reason
    """
    print("\nExiting: " + reason.__repr__())
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    # This point should be unreachable, just die already


def debug(channel: str, *args: Union[list,  str]):
    """Debugging print and logging functions

    Records information for debugging by printing or logging to disk. args is a
        list of arguments to be formatted. Various channels can be toggled on
        or off from settings.DEBUG_CHANNELS: dict. Channels not found
        in the dict while be printed by default.

    Usage:
    debug("channel", "message")
    debug("channel", object)
    debug("channel", "message: {}, {}", ["list", thing_to_format])

    respective outputs:
    channel: message
    channel: object.__repr__()
    channel: message with brackets: list, thing_to_format.__repr__()

    By formatting once inside debug(), format() is only called if printing is
    turned on. Remember to include [ ] around the items to be formatted.

    Note that one iteration of this code spawned a separte thread for every
    debug() call. The printing system call could not keep up and threads
    piled up and eventually crashed the program. Either threads must be
    managed with pools or print statements can be allowed to slow down the
    program (They can be turn off in settings)
    """

    # TODO: Use settings.ROLE for per client and server debugging
    if(settings.DEBUG_PRINTING and channel_active(channel)):
        n = len(args)
        # Print message to console
        if n == 1:
            print("{}:\t{}".format(channel, args[0]))
        elif n == 2:
            message = str(args[0])
            print("{}:\t{}".format(channel, message.format(*args[1])))
        elif 2 > 1:
            message = str(args[0])
            print("{}:\t{}".format(channel, message.format(*args[1:])))
    if(settings.DEBUG_LOGGING and channel_active(channel)):
        # TODO: Output stuff to a log file
        pass


def channel_active(channel: str) -> bool:
    """Whether to print or log for a debug channel

    Channels that are not found are debugged by default
    """
    if channel in settings.DEBUG_CHANNELS:
        val = settings.DEBUG_CHANNELS[channel]
        return val
    return True  # default for unknown channels


def sleep(time_s: Union[int, float]):
    """Pauses the execution of the thread for time_s seconds
    """
    if settings.DISABLE_SLEEP:
        debug("sleep", "Sleep disabled, not sleeping")
        return
    if time_s == 0:
        return

    time.sleep(time_s)


def debug_delay():
    sleep(settings.DEBUGGING_DELAY_S)


def init_dict(keys: List[str], val: Any) -> dict:
    d = {}
    for k in keys:
        d[k] = val
    return d


def attempt(action: Callable[[], bool],
            tries: int, fail_once: Callable,
            failure: Callable[[int], None]) -> None:
    """Wrapper for trying to complete and action with a number of tries
    Should follow this prototype:
    def attmpt_action():
        def try_action() -> bool:
            try:
                return True
            except Exception as error:
                debug("channel", "error: {}", [error.__repr__()])
                return False

        def fail_once() -> None:
            debug("action", "action failed, retrying")
            sleep(settings.ACTION_RETRY_WAIT)

        def failure(tries: int) -> None:
            if settings.REQUIRE_ACTION:
                exit("Could not do required action")
            else:
                debug("action", "Ignoring failing action after {} tries",
                      [tries])
                settings.USE_ACTION = False

        attempt(try_action, settings.ACTION_ATTEMPTS, fail_once, failure)
        debug("action", "Did action")
    """
    attempts = 1
    while (not action()):
        if attempts >= tries:
            failure(attempts)
            return
        fail_once()
        attempts += 1


class Profiler:
    def __init__(self):
        self.time_dict = {}
        self.moving_avg_len = settings.PROFILING_AVG_WINDOW_LEN

    def log_task(self, task_type: TaskType, runtime: float):
        # Make sure queue exists
        if self.time_dict.get(task_type) is None:
            self.init_task_type(task_type)
        # Shift elements
        self.time_dict[task_type].append(runtime)
        debug("profiling_avg", "Task {} has average runtime {}",
              [task_type, self.avg_time(task_type)])

    def init_task_type(self, task_type: TaskType):
        self.time_dict[task_type] = deque(maxlen=self.moving_avg_len)

    def avg_time(self, task_type: Union[TaskType, str]) -> float:
        return self.format_time(sum(self.time_dict[task_type]) /
                                len(self.time_dict[task_type]))

    def dump(self):
        debug("profiling_dump", "Type: \t\tAvg runtime: ")
        for k in self.time_dict.keys():
            debug("profiling_dump", "{}: {}", [k, self.avg_time(k)])

    def format_time(self, time_s: float) -> str:
        if time_s > 1:
            return "{:6.3f} s".format(time_s)
        elif time_s > 0.001:
            return "{:6.3f} ms".format(time_s * 1000)
        elif time_s > 0.000001:
            return "{:6.3f} us".format(time_s * 1000000)
        elif time_s > 0.000000001:
            return "{:6.3f} ns".format(time_s * 1000000000)

    def terminate(self):
        self.dump()
