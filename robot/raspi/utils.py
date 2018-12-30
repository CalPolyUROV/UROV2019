"""Various helping utilities used throughout the code

"""

# System imports
import os  # For exit
import sys  # For exit
import time  # For sleep
import _thread  # For  multi threaded debug
import random  # Simulated control values

# Our imports
import settings


def sleep(time_s: int):
    """Pauses the execution of the thread
    Do not use in production
    """
    # TODO: prevent use of this via a setting
    time.sleep(time_s)


def exit(reason: str):
    print("\nExiting: " + reason.__repr__())
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

# TODO: Use settings.ROLE for per client and server debugging
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
    turned on. Remember to include [ ] around the items to be formatted
    """
    if(settings.PRINTING and channel_active(channel)):
        n = len(args)
        # Print message to console
        if n == 1:
            print("{}:\t{}".format(channel, args[0]))
        elif n == 2:
            print("{}:\t{}".format(channel, args[0].format(*args[1])))
        elif 2 > 1:
            print("{}:\t{}".format(channel, args[0].format(*args[1:])))
    if(settings.LOGGING and channel_active(channel)):
        # TODO: Output stuff to a log file
        pass
        # Do NOT use printing on another thread because it is so slow 
        # that thread will pile up and the limit of number of threads will
        #  be reached

# Deprecated, use debug()
# def debug_f(channel: str, message: str, formatting: list):
#     if(settings.PRINTING and channel_active(channel)):
#         # TODO: Do this better
#         print("{}:\t{}".format(channel, message.format(*formatting)))
#     if (settings.LOGGING and channel_active(channel)):
#         # TODO: Output stuff to a log file
#         pass
#         # Do NOT use printing on another thread because it is so slow 
#         # that thread will pile up and the limit of number of threads will
#         #  be reached
#         # _thread.start_new_thread(log_f, (channel, message, formatting))

def channel_active(channel: str) -> bool:
    """Whether to print or log for a debug channel

    Channels that are not found are debugged by default
    """
    if channel in settings.DEBUG_CHANNELS:
        return settings.DEBUG_CHANNELS[channel]
    return True # default for unknown channels

# TODO: Add logging to a specific file
# (such as for logging the port that a sockets connection is on, so that the
#  value is accessible to the other Pi over a network share)
def log(channel: str, message: str):
    pass
    # TODO: Implement logging to disk


def log_f(channel: str, message: str, formatting: list):
    pass
    # TODO: Implement formatted logging to disk


# Simulation tools
def random_val():
    return random.randint(0, 1)
