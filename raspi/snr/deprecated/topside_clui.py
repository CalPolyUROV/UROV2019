# """Command Line User Interface
# Provides a visual interface for the terminal for the topside unit"""

# from typing import Callable

# import settings
# from snr.async_endpoint import AsyncEndpoint


# class TopsideClui(AsyncEndpoint):
#     def __init__(self, name: str, get_data: Callable):
#         if not settings.USE_TOPSIDE_CLUI:
#             debug("clui", "Not enabled in settings, not initializing CLUI")
#             return
#         super().__init__(name, self.refresh_ui, settings.TOPSIDE_UI_TICK_RATE)

#         self.get_data = get_data
#         self.init_ui()
#         self.loop()

#     def init_ui(self):
#         pass

#     def refresh_ui(self):
#         ui_data = self.get_data(self.name)
#         if ui_data is None:
#             debug("CLUI", "Data for UI is None, not refreshing")
#             return
#         button_a = ui_data.get("button_a")
#         bottom_line = "button_a: " + str(button_a)
#         print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" +
#               bottom_line, end='', flush=True)

#     def terminate(self):
#         debug("clui", "Terminating CLUI")
#         self.set_terminate_flag()
