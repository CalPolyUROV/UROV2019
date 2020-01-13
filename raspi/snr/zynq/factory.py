from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.node import Node


class ZyboFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str):
        super().__init__()
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name

    def get(self, parent: Node) -> Endpoint:
        from snr.zynq.zybo import Zybo
        return Zybo(parent, "Hardware IP Connection",
                    self.transmit_data_name,
                    self.query_data_name)

    def __repr__(self):
        return f"Zybo Factory({self.transmit_data_name}, {self.query_data_name})"
