from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.node import Node


class SerialFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str,
                 firmware_path: str):
        super().__init__()
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name
        # TODO: Support updating Arduino firmware on startup
        # self.firmware_path = firmware_path

    def get(self, parent: Node) -> Endpoint:
        from snr.comms.serial.serial_connection import SerialConnection
        return SerialConnection(parent, "Serial Connection",
                                self.transmit_data_name,
                                self.query_data_name)

    def __repr__(self):
        return "Serial Connection Factory"
