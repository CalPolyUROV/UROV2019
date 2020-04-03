from snr.endpoint import Endpoint
from snr.endpoint_factory import EndpointFactory
from snr.node import Node


class ControllerFactory(EndpointFactory):
    def __init__(self, output_data_name: str):
        super().__init__()
        self.output_data_name = output_data_name

    def get(self, parent: Node) -> Endpoint:
        from snr.io.controller.controller import Controller
        return Controller(parent, self.output_data_name)

    def __repr__(self):
        return "Controller Factory"
