from queue import Empty
from threading import Thread
from time import sleep
from typing import Union, Callable

# Injection
from multiprocessing import Queue as Queue

import settings

SLEEP_TIME = 0.005
# ~5 ms => 90 fps cap on debug messages being printed

# Whether created thread is a daemon.
DAEMON_THREAD = False


class Debugger:
    """Print debugging framework allowing any thread or process to send lines
    to be printed on stdout. Channels can be used to filter which messages are
    printed. Messages can be formatted.
    """

    def __init__(self):
        self.q = Queue()

        self.terminate_flag = False
        self.printing_thread = Thread(target=lambda:
                                      self.consumer(q=self.q,
                                                    action=print,
                                                    sleep_time=SLEEP_TIME),
                                      daemon=DAEMON_THREAD,
                                      )
        self.printing_thread.start()

    def consumer(self, q: Queue, action: Callable, sleep_time: int):
        """A method to be run by a thread for consuming the contents of a
        queue asynchronously
        """
        # Loop
        while not self.terminate_flag:
            try:
                # Consume line from queue
                line = None
                line = q.get_nowait()
                if line is not None:
                    # Perform action on item
                    action(line)
            except Empty:
                # Queue is empty
                pass
            except EOFError as e:
                # Handle pipes breaking inside libraries
                print(f"EOFError: {e}")
                self.terminate_flag = True
            # Wait a bit
            sleep(sleep_time)

        # Loop exited
        # Flush remaining lines
        try:
            # Consume line from queue
            line = None
            line = q.get_nowait()
            while line is not None:
                # Perform action on item
                action(line)
                line = None
                line = q.get_nowait()
        except Empty:
            # Queue is empty
            pass
        except Exception as e:
            print(f"Error flushing debug message queue: {e}")
        return

    def join(self):
        # Enable thread loop exit condition
        self.set_terminate_flag("join")
        # Wait for queue to be emptied
        # if_joinable(self.q, self.q.join)
        # Join thread
        self.printing_thread.join(timeout=0.5)

    def set_terminate_flag(self, reason: str):
        self.terminate_flag = True

    def debug(self, channel: str, *args: Union[list,  str]):
        """Debugging print and logging function

        Records information for debugging by printing or logging to disk.
            args is a list of arguments to be formatted. Various channels
            can be toggled on or off from settings.DEBUG_CHANNELS dict.
            Channels not found in the dict while be printed by default.

        Usage:
        // In constructor
        self.dbg = debug  // localize parameter for ease of use

        // later
        self.dbg("channel", "message")
        self.dbg("channel", object)
        self.dbg("channel",
                 "message: {}, {}",
                 ["list", thing_to_format]) // Respect line limit

        respective outputs:
        [channel]   message
        [channel]   object.__repr__()
        [channel]   message with brackets: list, thing_to_format.__repr__()

        By formatting once inside debug(), format() is only called if
        printing is turned on. Remember to include [ ] around the items
        to be formatted.

        A single thread handles all calls by consuming a Queue.
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
