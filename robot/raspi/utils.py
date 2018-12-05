
# System imports
import os  # For exit
import sys  # For exit
import time  # For sleep
import _thread  # For  multi threaded debug

# Our imports
import settings


def sleep(time_s: int):
    time.sleep(time_s)


def exit():
    print(': Interrupted, exiting')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


"""Debugging print and logging functions
"""

"""Usage:
debug("channel", "message")
debug("channel", object)
debug_f("channel", "message with brackets: {}, {}", ["list", of_things_to_format_in])

equivelant to (don't do the following):
    debug("channel", "message with brackets: {}, {}".format("list", of_things_to_format_in)
By formatting once inside debug_f(), format() is only called if printing is turned on.
"""

# TODO: Use settings.ROLE for per client and server debugging


def debug(channel: str, message: str):
    if(settings.CHANNELS[channel]):
        _thread.start_new_thread(_seq_debug, (channel, message))


def debug_f(channel: str, message: str, formatting: list):
    if(settings.CHANNELS[channel]):
        _thread.start_new_thread(seq_debug_f, (channel, message, formatting))


def _seq_debug(channel: str, message: str):
    if(settings.PRINTING):
        # Print message to console
        print("{}:\t{}".format(channel, message))
    if(settings.LOGGING):
        # TODO: Output stuff to a log file
        pass


def seq_debug_f(channel: str, message: str, formatting: list):
    if(settings.PRINTING):
        # TODO: Do this better
        print("{}:\t{}".format(channel, message.format(*formatting)))
    if(settings.LOGGING):
        # TODO: Output stuff to a log file
        pass
