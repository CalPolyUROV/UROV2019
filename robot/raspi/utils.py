"""Various helper utilities used throughout the code
Attempts to document propper usage of such functions
"""

# System imports
import os  # For exit
import random  # Simulated control values
import sys  # For exit
import time  # For sleep
from typing import Callable, NewType, Dict
import _thread  # For  multi threaded debug

# Our imports
import settings


def sleep(time_s: int) -> None:
    """Pauses the execution of the thread for time_s seconds
    """
    # TODO: prevent use of this via a setting
    time.sleep(time_s)


def print_usage() -> None:
    """Prints a Unix style uasge message on how to start the program
    """
    print("usage: python3.5 main.py (robot | topside)")


def exit(reason: str) -> None:
    """Kills the program after printing the supplied str reason
    """
    print("\nExiting: " + reason.__repr__())
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    # This point should be unreachable, just die already

def debug_delay():
    sleep(settings.DEBUGGING_DELAY_S)


def debug(channel: str, *args):
    """Debugging print and logging functions

    Records information for debugging by printing or logging to disk. args is a
        list of arguments to be formatted. Various channels can be toggled on or
        off from settings.DEBUG_CHANNELS: dict. Channels not found in the dict
        while be printed by default.

    Usage:
    debug("channel", "message")
    debug("channel", object)
    debug("channel", "message with brackets: {}, {}", ["list", thing_to_format])

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
            print("{}:\t{}".format(channel, args[0].format(*args[1])))
        elif 2 > 1:
            print("{}:\t{}".format(channel, args[0].format(*args[1:])))
    if(settings.DEBUG_LOGGING and channel_active(channel)):
        # TODO: Output stuff to a log file
        def log(channel: str, message: str):
            """Unimplemented logging function
            """
            # TODO: Add logging to a specific file
            # (such as for logging the port that a sockets connection is on, so that the
            #  value is accessible to the other Pi over a network share)
            pass
        debug("framework", "Logging to file is not implemented")
        pass


def channel_active(channel: str) -> bool:
    """Whether to print or log for a debug channel

    Channels that are not found are debugged by default
    """
    if channel in settings.DEBUG_CHANNELS:
        val = settings.DEBUG_CHANNELS[channel]
        if isinstance(val, bool):
            return val
        else:
            return  val < settings.DEBUG_LEVEL
    return True  # default for unknown channels


# Simulation tools
def random_val():
    """Generates random values for simulated control input
    """
    # TODO: Account for different kinds of input data such as joysticks vs buttons
    return random.randint(0, 1)


def try_key(d: dict, k: str):
    """Mapping dict may not contain a key to lookup, handle it
    """
    try:
        return d[k]
    except (KeyError):
        debug("controls_reader", "Unknown control key: ", [k])
        # TODO: Investigate changing this behavior
        return "Key not supplied in mapping: " + k


Attemptable = NewType("Attemptable", Callable[[None], bool])


def attempt(action: Attemptable, tries: int, fail_once: Callable, failure: Callable[[int], None]) -> None:
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
                debug("action", "Ignoring failing action after {} tries", [tries])
                settings.USE_ACTION = False

        attempt(try_action, settings.ACTION_ATTEMPTS, fail_once, failure)
        debug("action", "Did action")
    """
    attempts = 1
    while (not action()):
        if attempts >= tries:
            failure(attempts)
            return
        else:
            fail_once()
            attempts += 1

# def switch(input: object, option_action_dict: Dict[object, Callable], default_action: Callable):
#     if input in option_action_dict:
#         option_action_dict[input]()
#     else:
#         default_action()
#     return

# def match(input: object, option_a, action_a, option_b: Callable, action_b: Callable):
#     if input is option_a or input == option_a:
#         action_a(input)
#     elif input is option_b or input == option_b:
#         action_b(input)

