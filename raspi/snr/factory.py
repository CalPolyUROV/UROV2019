from typing import List, Tuple

from snr.datastore import Datastore
from snr.endpoint import Endpoint
from snr.task import SomeTasks, Task, TaskHandler, TaskSource, TaskType
from snr.utils import Profiler, debug, pass_fn


class Factory:
    def __init__(self):
        pass

    def get(self, mode: str,
            profiler: Profiler,
            datastore: Datastore) -> Endpoint:
        raise NotImplementedError


# class TemplateFactory(Factory):
#     def __init__(self, stuff: str):
#         super().__init__()
#         self.stuff = stuff

#     def get(self, mode: str,
#             profiler: Profiler,
#             datastore: Datastore) -> Endpoint:
#         return Endpoint(mode, profiler, datastore, stuff)

