from snr.task import SomeTasks, Task
from snr.node import Node


class Endpoint:
    def __init__(self, parent: Node, name: str):
        self.parent = parent
        self.name = name

    def get_new_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.name
