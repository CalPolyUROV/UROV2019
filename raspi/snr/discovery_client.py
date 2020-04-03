import socket
from typing import Callable, List

import settings

TIMEOUT = 2

context = "discovery_client"


class DiscoveryClient:
    def __init__(self, debug: Callable):
        self.dbg = debug

    def find_me(self, my_name: str, hosts: List[str]):
        self.dbg(context,
                 "Discovering local node local ip from {}",
                 [hosts])
        for host in hosts:
            self.dbg(context + "_verbose",
                     "Checking host {}", [host])
            node_name = self.ping(host)
            if node_name == my_name:
                self.dbg("node_info",
                         "Identified self as {}",
                         [host])
                return host

    def ping(self, target_host: str) -> str:
        """Blocking call to discovery an SNR Node running on a host.
        Returns a node name if the node discovery server responds,
        or None on timeout or error
        """
        host_tuple = (target_host, settings.DISCOVERY_SERVER_PORT)
        try:
            s = socket.create_connection(host_tuple,
                                         settings.SOCKETS_CLIENT_TIMEOUT)
            # Reuse port prior to slow kernel release
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            data = s.recv(settings.MAX_SOCKET_SIZE).decode()
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except (Exception, socket.timeout) as e:
            self.dbg(context + "_warning",
                     "Failed to discover node at {}:{}: {}",
                     [host_tuple[0], host_tuple[1], e])
            data = None

        return data
