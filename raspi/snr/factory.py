from typing import List, Tuple

from snr.task import SomeTasks, Task, TaskHandler, TaskSource, TaskType
from snr.utils import debug, pass_fn


TaskCallablesTuple = Tuple[List[TaskSource],
                           List[TaskHandler],
                           list]


class Factory:
    def __init__(self, get_tasks: TaskSource, task_handler: TaskHandler,
                 endpoints: list):
        self.get_tasks = get_tasks
        self.task_handler = task_handler
        self.endpoints = endpoints

    def get_task_callables(self, mode: str) -> TaskCallablesTuple:
        return self.get_tasks, self.task_handler, self.endpoints


class EthernetLink:
    def __init__(self, server_port: int, client_port: int, data_name: str):
        self.server_port = server_port
        self.client_port = client_port
        self.data_name = data_name

        self.server = EthServerFactory(self)
        self.client = EthClientFactory(self)


class EthServerFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__(pass_fn, pass_fn, pass_fn)
        self.link = link


class EthClientFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__(pass_fn, pass_fn, pass_fn)
        self.link = link


class RobotMotorsFactory(Factory):
    def __init__(self, input_data_name: str,
                 output_data_name: str):
        super().__init__(pass_fn, pass_fn, pass_fn)
        self.input_data_name = input_data_name
        self.output_data_name = output_data_name


