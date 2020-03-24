from typing import List

from snr.dds.dds import DDS
from snr.dds.dds_connection import DDSConnection
from snr.dds.sockets.sockets_dds import SocketsConfig, SocketsDDS
from snr.dds_factory import DDSFactory
from snr.endpoint import Endpoint
from snr.factory import Factory


class EthernetLink(DDSFactory):
    def __init__(self, hosts: List[str], server_port: int):
        self.hosts = hosts
        self.server_port = server_port

    def get(self, parent_node) -> List[DDSConnection]:
        remote_hosts = self.select_remote_host(parent_node.get_node_ip())
        return [SocketsDDS(SocketsConfig(remote_host, self.server_port))
                for remote_host in remote_hosts]

    def select_remote_host(self, local_host) -> str:
        """Removes the local host from the hosts in the group
        """
        remote_hosts = []
        for h in self.hosts:
            if h is not local_host:
                remote_hosts.add(h)
        return h
