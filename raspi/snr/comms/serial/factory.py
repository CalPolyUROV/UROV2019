from snr.comms.serial.serial_connection import SerialConnection
from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.node import Node


class SerialFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str,
                 firmware_path: str):
        super().__init__()
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name
        self.firmware_path = firmware_path  # Not used

    def get(self, parent: Node) -> Endpoint:
        return SerialConnection(parent,
                                self.transmit_data_name,
                                self.query_data_name)
