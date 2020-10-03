from typing import List

from snr.dds.sockets.sockets_dds import SocketsConfig, SocketsDDS
from snr.dds.factory import DDSFactory

context = "sockets_dds_fac"


class EthernetLink(DDSFactory):
    def __init__(self, hosts: List[str], server_port: int):
        self.hosts = hosts
        self.server_port = server_port

    def get_connections(self, parent_node=None, parent_dds=None):
        self.dbg = parent_node.dbg

        local_host = parent_node.get_local_ip()
        self.dbg(context,
                 "Selecting remote hosts from {} (skipping local: {})",
                 [self.hosts, local_host])
        connections = []
        for host in self.hosts:
            if host is not local_host:
                connections.append(SocketsDDS(parent_node,
                                              SocketsConfig(host,
                                                            self.server_port),
                                              parent_dds.inbound_store))

        self.dbg(context, "Prepared DDS Connections:\n{}", [connections])
        return connections

    def __repr__(self):
        return f"Ethernet Link Factory: {self.hosts}:{self.server_port}"
