from typing import Callable

from snr.factory import Factory
from snr.io.controller.controller import Controller
from snr.utils import pass_fn, Profiler


class ControllerFactory(Factory):
    def __init__(self, output_data_name: str):
        super().__init__(pass_fn, pass_fn, self.get_endpoint)
        self.output_data_name = output_data_name

    def get_endpoint(self, store_data: Callable, profiler: Profiler):
        return Controller(self.output_data_name, store_data, profiler)
