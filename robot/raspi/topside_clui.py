"""Command Line User Interface
Provides a visual interface for the terminal"""

# System imports
from typing import Callable

# Our imports
import settings
from snr import AsyncEndpoint
from utils import debug


class TopsideClui(AsyncEndpoint):
    def __init__(self, name: str, get_data: Callable):
        if not settings.USE_TOPSIDE_CLUI:
            debug("clui", "Not enabled in settings, not initializing CLUI")
            return
        super().__init__(name, self.refresh_ui, settings.TOPSIDE_UI_TICK_RATE)

        self.get_data = get_data
        self.init_ui()
        self.loop()

    def init_ui(self):
        pass

    def refresh_ui(self):
        controller_data = self.get_data(settings.CONTROLLER_NAME)
        if controller_data is not None:
            button_a = controller_data["button_a"]
        else:
            button_a = ""
        bottom_line = "button_a: " + str(button_a)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" + bottom_line, end='', flush=True)

    def terminate(self):
        debug("clui", "Terminating CLUI")
        self.set_terminate_flag()
