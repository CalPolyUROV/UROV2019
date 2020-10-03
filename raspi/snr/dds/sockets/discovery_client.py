import socket
from typing import List, Tuple

from snr.dds.sockets.discovery_server import DiscoveryServer
from snr.debug import Debugger
from snr.context import Context

TIMEOUT = 2


class DiscoveryClient(Context):
    def __init__(self, parent_context: Context):
        super().__init__("discovery_client", parent_context)

    def find_me(self,
                local_role: str,
                hosts: List[str]
                ) -> Tuple[str, List[str]]:

        self.log("Discovering local node ip from {}",
                 [hosts])

        discovery_server = DiscoveryServer(self,
                                           local_role,
                                           self.settings.DISCOVERY_SERVER_PORT)

        local_host = None

        for host in hosts:
            self.dbg("Checking host '{}'", [host])
            node_name = self.ping((host, discovery_server.port))
            if node_name == local_role:
                self.log("Identified self as '{}'",
                         [host])
                local_host = host
                break

        discovery_server.terminate()
        self.log("Discovered self to be '{}', removeing from hosts: {}",
                 [local_host, hosts])
        hosts.remove(local_host)
        return (local_host, hosts)

    def ping(self, target_host_tuple: Tuple[str, int]) -> str:
        """Blocking call to discovery an SNR Node running on a host.
        Returns a node name if the node discovery server responds,
        or None on timeout or error
        """
        try:
            s = socket.create_connection(target_host_tuple,
                                         self.settings.SOCKETS_CLIENT_TIMEOUT)
            # Reuse port prior to slow kernel release
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            data = s.recv(self.settings.MAX_SOCKET_SIZE).decode()
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            s = None
        except (Exception, socket.timeout) as e:
            self.warn("Did not find node at {}:{}: {}",
                      [target_host_tuple[0], target_host_tuple[1], e])
            data = None

        return data
