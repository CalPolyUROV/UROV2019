from snr.task import SomeTasks, Task
from snr.utils.utils import no_op


class Endpoint:
    def __init__(self, parent_node, name: str):
        self.parent = parent_node
        if self.parent:
            self.dbg = parent_node.dbg
        else:
            self.dbg = no_op
        self.name = name

    def get_new_tasks(self) -> SomeTasks:
        return None

    def task_handler(self, t: Task) -> SomeTasks:
        return None

    def set_terminate_flag(self, reason: str):
        pass

    def terminate(self):
        self.dbg("framework_warning",
                 "{} does not implement terminate()",
                 [self.name])
        raise NotImplementedError

    def join(self):
        return

    def __repr__(self) -> str:
        return self.name
