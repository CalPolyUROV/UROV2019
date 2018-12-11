
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
    print(': ' + reason)
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


"""Debugging print and logging functions
"""

"""Usage:
debug("channel", "message")
debug("channel", object)
debug_f("channel", "message with brackets: {}, {}", ["list", of_things_to_format])

equivelant to (don't do the following):
    debug("channel", "message with brackets: {}, {}".format("list", of_things_to_format_in)

By formatting once inside debug_f(), format() is only called if printing is turned on.
Remember to include [ ] around  
"""

# TODO: Use settings.ROLE for per client and server debugging


def debug(channel: str, message: str):
    if(settings.DEBUG_CHANNELS[channel]):
        if(settings.PRINTING):
            # Print message to console
            print("{}:\t{}".format(channel, message))
        if(settings.LOGGING):
            # TODO: Output stuff to a log file
            pass
            # Do NOT use printing on another thread because it is so slow 
            # that thread will pile up and the limit of number of threads will
            #  be reached
            # _thread.start_new_thread(log, (channel, message))


def debug_f(channel: str, message: str, formatting: list):
    if(settings.DEBUG_CHANNELS[channel]):
        if(settings.PRINTING):
            # TODO: Do this better
            print("{}:\t{}".format(channel, message.format(*formatting)))
        if (settings.LOGGING):
            # TODO: Output stuff to a log file
            pass
            # Do NOT use printing on another thread because it is so slow 
            # that thread will pile up and the limit of number of threads will
            #  be reached
            # _thread.start_new_thread(log_f, (channel, message, formatting))


# TODO: Add logging to a specific file
# (such as for logging the port that a sockets connection is on, so that the
#  value is accessible to the other Pi over a network share)
def log(channel: str, message: str):
    pass
    # TODO: Implement logging to disk


def log_f(channel: str, message: str, formatting: list):
    pass
    # TODO: Implement logging to disk


# Simulation tools
def random_val():
    return random.randint(0, 1)
