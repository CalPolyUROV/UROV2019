from snr.task import SomeTasks, Task
from snr.node import Node


class Endpoint:
    def __init__(self, parent: Node):
        self.parent = parent

    def get_new_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, task: Task) -> SomeTasks:
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError
