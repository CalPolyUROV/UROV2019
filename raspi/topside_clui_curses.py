"""Command Line User Interface
Provides a visual interface for the terminal"""

# System imports
from typing import Callable
from curses import wrapper

# Our imports
import settings
from snr_lib import AsyncEndpoint
from snr_utils import debug


class TopsideCluiCurses(AsyncEndpoint):
    def __init__(self, name: str, get_data: Callable):
        if not settings.USE_TOPSIDE_CLUI:
            debug("clui", "Not enabled in settings, not initializing CLUI")
            return
        super().__init__(name, self.wrap, settings.TOPSIDE_UI_TICK_RATE)

        self.get_data = get_data
        self.init_ui()
        self.loop()

    def init_ui(self):
        pass

    def wrap(self):
        wrapper(self.refresh_ui)
        return

    def refresh_ui(self, stdscr):
        debug("clui", "Refreshing UI")
        stdscr.refresh()
        stdscr.addstr(0, 0, "HELLO WORLD")

        stdscr.refresh()

    def terminate(self):
        debug("clui", "Terminating CLUI")
        self.set_terminate_flag()
