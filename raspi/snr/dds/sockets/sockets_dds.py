from typing import Callable, List

from snr.dds.dds_connection import DDSConnection
from snr.comms.sockets.config import SocketsConfig
from snr.dds.page import Page
from snr.dds.sockets.config import SocketsConfig
from snr.dds.sockets.server import SocketsServer
from snr.dds.sockets.client import SocketsClient
from snr.dds_factory import DDSFactory
from snr.utils.utils import no_op
from snr.discovery_client import DiscoveryClient
from snr.context import Context

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
    def __init__(self,
                 hosts: List[str],
                 port: int):
        super().__init__()
        self.hosts = hosts
        self.port = port

    def get(self, parent_node=None):
        if parent_node:
            local_ip, hosts = DiscoveryClient(
                parent_node).find_me(
                parent_node.role,
                self.hosts)
            inbound_store = parent_node.datastore.inbound_store
            inbound_store("node_ip_address", local_ip)
            parent_node.info("Assigned {} node ip: {}",
                             [parent_node.name, local_ip])
            return [SocketsDDS(config=SocketsConfig(host, self.port),
                               inbound_store=inbound_store)
                    for host in hosts]
        else:
            return []


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
