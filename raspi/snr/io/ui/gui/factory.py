from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.io.controller.controller import Controller
from snr.node import Node


class GUIFactory(Factory):
    def __init__(self, input_data_name: str):
        super().__init__()
        self.input_data_name = input_data_name

    def get(self, parent: Node) -> Endpoint:
        from snr.io.ui.gui.gui_endpoint import SimpleGUI
        return SimpleGUI(parent, "gui", self.input_data_name)
