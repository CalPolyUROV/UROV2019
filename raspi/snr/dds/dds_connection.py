from snr.utils.utils import no_op
from typing import Callable
from snr.dds.page import Page


class DDSConnection:
    def __init__(self):
        self.inbound_store = no_op

    def set_inbound_store(self,
                          inbound_store: Callable[[Page], None]):
        self.inbound_store = inbound_store

    def send(self):
        raise NotImplementedError

    def recieve(self, page: Page):
        self.inbound_store(page)
