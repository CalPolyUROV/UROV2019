from typing import List
# from snr.node import Node


class Factory:
    def __init__(self):
        pass

    def get(self, parent_node=None) -> List:
        raise NotImplementedError



"""Example factory that might be implemented for an endpoint
"""
# class TemplateFactory(Factory):
#     def __init__(self, stuff: str):
#         super().__init__()
#         self.stuff = stuff

#     def get(self, mode: str,
#             profiler: Profiler,
#             datastore: Datastore) -> Endpoint:
#         return Endpoint(mode, profiler, datastore, stuff)
