from typing import Callable

from snr.dds.dds_connection import DDSConnection
from snr.comms.sockets.config import SocketsConfig
from snr.dds.page import Page
from snr.dds.sockets.server import SocketsServer
from snr.dds.sockets.client import SocketsClient
from snr.dds_factory import DDSFactory
from snr.utils.utils import no_op


"""
DDS
-----------------------
send(), inbound_store()
-----------------------
SocketsDDS(DDS Connection)
Client - consumer thread
Server - DDS tx consumer thread
"""


class SocketsDDSFactory(DDSFactory):
    def __init__(self, config: SocketsConfig):
        super().__init__()
        self.config = config

    def get(self, parent_node=None):
        if not parent_node:
            inbound_store = no_op
        else:
            inbound_store = parent_node.datastore.inbound_store
        return SocketsDDS(self.config, inbound_store)


class SocketsDDS(DDSConnection):
    def __init__(self, parent_node,
                 config: SocketsConfig,
                 inbound_store: Callable):
        super().__init__(inbound_store)

        self.server = SocketsServer(parent_node,
                                    config,
                                    callback=self.inbound_store)
        # start receive thread
        self.client = SocketsClient(parent_node, config)
        # setup sending thread

    def send(self, data: Page):
        self.client.send_data(data)
