from typing import List

from snr.dds.dds_connection import DDSConnection
from snr.factory import Factory


class DDSFactory(Factory):
    def __init__(self):
        pass

    def get(self, parent_node=None):
        return self.get_connections(parent_node)

    def get_connections(self, parent_node=None) -> List[DDSConnection]:
        raise NotImplementedError
