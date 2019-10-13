from snr.task import TaskHandler, TaskSource, SomeTasks


class Endpoint:
    def __init__(self):
        pass

    def get_new_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, task) -> SomeTasks:
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError
