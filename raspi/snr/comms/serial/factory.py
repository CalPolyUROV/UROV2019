from snr.comms.serial.serial_connection import SerialConnection
from snr.utils import pass_fn
from snr.factory import Factory


class SerialFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str,
                 firmware_path: str):
        super().__init__(pass_fn, pass_fn, self.get_endpoints)
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name
        self.firmware_path = firmware_path  # Not used

    def get_endpoints(self) -> list:
        return [SerialConnection()]
