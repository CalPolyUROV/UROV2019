from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.node import Node


class ControllerFactory(Factory):
    def __init__(self, output_data_name: str):
        super().__init__()
        self.output_data_name = output_data_name

    def get(self, parent: Node) -> Endpoint:
        # Wait until later to import pygame depenacy to
        #  prevent crash when not present on robot
        from snr.io.controller.controller import Controller
        return Controller(parent, self.output_data_name)

    def __repr__(self):
        return "Controller Factory"
