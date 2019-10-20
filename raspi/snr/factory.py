from snr.endpoint import Endpoint
from snr.node import Node


class Factory:
    def __init__(self):
        pass

    def get(self, parent: Node) -> Endpoint:
        raise NotImplementedError


# class TemplateFactory(Factory):
#     def __init__(self, stuff: str):
#         super().__init__()
#         self.stuff = stuff

#     def get(self, mode: str,
#             profiler: Profiler,
#             datastore: Datastore) -> Endpoint:
#         return Endpoint(mode, profiler, datastore, stuff)
