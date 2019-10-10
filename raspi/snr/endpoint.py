from snr.factory import Factory
from snr.task import TaskHandler, TaskSource


class Endpoint(Factory):
    def __init__(self, get_tasks: TaskSource, task_handler: TaskHandler,
                 endpoint):
        super().__init__(get_tasks, task_handler, endpoint)
