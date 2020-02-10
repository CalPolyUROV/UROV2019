from snr.task import SomeTasks, Task
from snr.node import Node
from snr.utils import debug


class Endpoint:
    def __init__(self, parent: Node, name: str):
        self.parent = parent
        self.dbg = parent.dbg
        self.name = name

    def get_new_tasks(self) -> SomeTasks:
        return None

    def task_handler(self, t: Task) -> SomeTasks:
        return None

    def set_terminate_flag(self):
        self.terminate()

    def terminate(self):
        self.dbg("framework_warning",
                 "{} does not implement terminate()",
                 [self.name])
        raise NotImplementedError

    def join(self):
        return

    def __repr__(self) -> str:
        return self.name
