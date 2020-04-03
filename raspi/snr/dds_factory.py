from typing import List

from snr.dds.dds_connection import DDSConnection
from snr.dds.dds import DDS
from snr.factory import Factory


class DDSFactory(Factory):
    def __init__(self):
        pass

    def get(self,
            parent_node=None,
            parent_dds: DDS = None):
        return self.get_connections(parent_node, parent_dds)

    def get_connections(self,
                        parent_node=None,
                        parent_dds: DDS = None) -> \
            List[DDSConnection]:
        raise NotImplementedError
