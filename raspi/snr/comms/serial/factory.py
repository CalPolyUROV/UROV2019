from snr.comms.serial.serial_connection import SerialConnection
from snr.utils import pass_fn, Profiler
from snr.factory import Factory
from snr.datastore import Datastore
from snr.endpoint import Endpoint


class SerialFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str,
                 firmware_path: str):
        super().__init__()
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name
        self.firmware_path = firmware_path  # Not used

    def get(self, mode: str,
            profiler: Profiler,
            datastore: Datastore) -> Endpoint:
        return SerialConnection(mode, profiler, datastore,
                                self.transmit_data_name,
                                self.query_data_name)
