from snr.utils.utils import no_op
from typing import Callable
from snr.dds.page import Page


class DDSConnection:
    def __init__(self, inbound_store=no_op):
        self.inbound_store = inbound_store

    def send(self, data: Page):
        raise NotImplementedError
