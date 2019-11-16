from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.io.controller.controller import Controller
from snr.node import Node
from ui.gui.GUI import start_GUI


class GUIFactory(Factory):
    def __init__(self, input_data_name: str):
        super().__init__()
        self.input_data_name = input_data_name

    def get(self, parent: Node) -> Endpoint:
        return start_GUI(parent, "gui", self.input_data_name)
