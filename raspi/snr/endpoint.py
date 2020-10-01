from snr.context import Context
from snr.task import SomeTasks, Task
from snr.utils.utils import no_op


class Endpoint(Context):
    def __init__(self, parent_context: Context, name: str):
        super().__init__(name, parent_context)

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
