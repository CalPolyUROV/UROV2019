from typing import List

from snr.endpoint import Endpoint
from snr.factory import Factory
from snr.task import Task, SomeTasks
from snr.node import Node


context = "recorder"


class Recorder(Endpoint):
    def __init__(self, parent_node, name: str, data_names: List[str]):
        super().__init__(parent_node, name)
        self.data_names = data_names
        self.dbg = parent_node.dgb

    def task_handler(self, t: Task) -> SomeTasks:
        self.dbg(context, "Recording task: {}", [t])
        return None


class RecorderFactory(Factory):
    def __init__(self, name: str, data_names: List[str]):
        super().__init__()
        self.name = name
        self.data_names = data_names

    def get(self, parent_node: Node) -> Recorder:
        return Recorder(parent_node, self.name, self.data_names)