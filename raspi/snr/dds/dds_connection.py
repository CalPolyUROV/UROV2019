from snr.context import Context
from snr.utils.utils import no_op
from typing import Callable
from snr.dds.page import Page


class DDSConnection(Context):
    def __init__(self,
                 name: str,
                 parent_context: Context,
                 inbound_store: Callable = no_op):
        super().__init__(name, parent_context)
        self.inbound_store = inbound_store

    def send(self, data: Page):
        raise NotImplementedError
