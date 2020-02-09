from multiprocessing import Queue
from threading import Thread
from time import sleep
from typing import Union

import settings

SLEEP_TIME = 0.001


class Debugger:
    def __init__(self):
        self.q = Queue()
        self.printing_thread = Thread(target=self.threaded_method,
                                      #   args=self.q,
                                      daemon=True)
        self.printing_thread.start()

    def threaded_method(self):
        while True:
            line = self.q.get()
            if line is not None:
                print(line)
            sleep(SLEEP_TIME)

    def debug(self, channel: str, *args: Union[list,  str]):
        """Debugging print and logging functions

        Records information for debugging by printing or logging to disk.
            args is a list of arguments to be formatted. Various channels
            can be toggled on or off from settings.DEBUG_CHANNELS: dict.
            Channels not found in the dict while be printed by default.

        Usage:
        debug("channel", "message")
        debug("channel", object)
        debug("channel", "message: {}, {}", ["list", thing_to_format])

        respective outputs:
        [channel] message
        [channel] object.__repr__()
        [channel] message with brackets: list, thing_to_format.__repr__()

        By formatting once inside debug(), format() is only called if
        printing is turned on. Remember to include [ ] around the items
        to be formatted.

        Note that one iteration of this code spawned a separte thread for every
        debug() call. The printing system call could not keep up and threads
        piled up and eventually crashed the program. Either threads must be
        managed with pools or print statements can be allowed to slow down the
        program (They can be turn off in settings)
        """

        # TODO: Use settings.ROLE for per client and server debugging?
        if(settings.DEBUG_PRINTING and self.channel_active(channel)):
            n = len(args)
            # Print message to console
            if n == 1:
                s = "[{}]\t\t{}".format(channel,
                                        args[0])
                self.q.put(s)
                # print(s)
            elif n == 2:
                message = str(args[0])
                s = "[{}]\t{}".format(channel,
                                      message.format(*args[1]))
                self.q.put(s)
                # print(s)
            elif 2 > 1:
                message = str(args[0])
                s = "[{}]\t{}".format(channel,
                                      message.format(*args[1:]))
                self.q.put(s)
                # print(s)
        if(settings.DEBUG_LOGGING and channel_active(channel)):
            # TODO: Output stuff to a log file
            pass

    def channel_active(self, channel: str) -> bool:
        """Whether to print or log for a debug channel

        Channels that are not found are debugged by default
        """
        if channel in settings.DEBUG_CHANNELS:
            val = settings.DEBUG_CHANNELS[channel]
            return val
        return True  # default for unknown channels
