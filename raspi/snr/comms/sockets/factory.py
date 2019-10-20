from snr.factory import Factory
from snr.comms.sockets.server import SocketsServer
from snr.comms.sockets.client import SocketsClient
from snr.comms.sockets.config import SocketsConfig
from snr.endpoint import Endpoint
from snr.node import Node


class EthernetLink:
    def __init__(self, server_port: int, client_port: int, data_name: str):
        self.server_port = server_port
        self.client_port = client_port
        self.data_name = data_name

        self.server = EthServerFactory(self)
        self.client = EthClientFactory(self)


class EthServerFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__()
        self.link = link

    def get(self, parent: Node) -> Endpoint:

        # TODO: Get proper socket requirement value
        config = SocketsConfig(parent.datastore.get("node_ip_address"),
                               self.link.server_port, False)

        return SocketsServer(parent, config, self.link.data_name)


class EthClientFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__()
        self.link = link

    def get(self, parent: Node) -> Endpoint:
        config = SocketsConfig(parent.datastore.get("node_ip_address"),
                               self.link.client_port, False)
        return SocketsClient(parent, config, self.link.data_name)
