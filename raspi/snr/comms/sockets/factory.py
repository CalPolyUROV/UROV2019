from typing import List

from snr.dds.dds import DDS
from snr.dds.dds_connection import DDSConnection
from snr.dds.sockets.sockets_dds import SocketsConfig, SocketsDDS
from snr.dds_factory import DDSFactory
from snr.endpoint import Endpoint
from snr.factory import Factory

context = "sockets_dds_fac"


class EthernetLink(DDSFactory):
    def __init__(self, hosts: List[str], server_port: int):
        self.hosts = hosts
        self.server_port = server_port

    def get(self, parent_node, parent_dds) -> List[DDSConnection]:
        self.dbg = parent_node.dbg

        local_host = parent_node.get_local_ip()
        self.dbg(context,
                 "Selecting remote hosts from {} (local: {})",
                 [self.hosts, local_host])
        remote_hosts = self.select_remote_host(local_host)
        connections = []
        for remote_host in remote_hosts:
            connections.append(SocketsDDS(parent_node,
                                          SocketsConfig(remote_host,
                                                        self.server_port),
                                          parent_dds.inbound_store))

        self.dbg(context, "Prepared DDS Connections:\n{}", connections)
        return connections

    def select_remote_host(self, local_host) -> str:
        """Removes the local host from the hosts in the group
        """
        remote_hosts = []
        for h in self.hosts:
            if h is not local_host:
                remote_hosts.append(h)
        return h
