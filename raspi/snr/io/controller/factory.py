from typing import Callable

from snr.datastore import Datastore
from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.io.controller.controller import Controller
from snr.utils import Profiler, pass_fn


class ControllerFactory(Factory):
    def __init__(self, output_data_name: str):
        super().__init__()
        self.output_data_name = output_data_name

    def get(self, mode: str,
            profiler: Profiler,
            datastore: Datastore) -> Endpoint:
        return Controller(mode, profiler, datastore,
                          self.output_data_name)
