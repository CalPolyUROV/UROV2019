from snr.endpoint import Endpoint
from snr.task import SomeTasks, Task
from snr.node import Node


class Zybo(Endpoint):
    def __init__(self, parent: Node, name: str,
                 input: str, output: str):
        super().__init__(parent, name)
        self.input = input
        self.output = output

    def get_new_tasks(self) -> SomeTasks:
        # TODO: Match serial task generation
        return None

    def task_handler(self, t: Task) -> SomeTasks:
        # TODO: Match serial task handling
        return None

    def terminate(self):
        # No need to deconstruct/close in any weird way (yet)
        pass
