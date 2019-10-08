from typing import List, Tuple

from snr.task import Handler, TaskSource, SomeTasks, Task
from snr.async_endpoint import AsyncEndpoint

TaskCallablesTuple = Tuple[List[TaskSource],
                           List[Handler],
                           List[AsyncEndpoint]]


class Factory:
    def __init__(self, get_tasks: TaskSource, task_handler: Handler,
                 async_endpoints: List[AsyncEndpoint]):
        self.get_tasks = get_tasks
        self.task_handler = task_handler
        self.async_endpoints = async_endpoints

    def get_task_callables(self, mode: str) -> TaskCallablesTuple:
        return self.get_tasks, self.task_handler, self.async_endpoints


class EthernetLink:
    def __init__(self, server_port: int, client_port: int, data_name: str):
        self.server_port = server_port
        self.client_port = client_port
        self.data_name = data_name

        self.server = EthServerFactory(self)
        self.client = EthClientFactory(self)


class EthServerFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__(self.get_tasks, self.task_handler, [])
        self.link = link

    def get_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass


class EthClientFactory(Factory):
    def __init__(self, link: EthernetLink):
        super().__init__(self.get_tasks, self.task_handler, [])
        self.link = link

    def get_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass


class SerialFactory(Factory):
    def __init__(self, transmit_data_name: str, query_data_name: str,
                 firmware_path: str):
        super().__init__(self.get_tasks, self.task_handler, [])
        self.transmit_data_name = transmit_data_name
        self.query_data_name = query_data_name
        self.firmware_path = firmware_path  # Not used

    def get_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass



class RobotMotorsFactory(Factory):
    def __init__(self, input_data_name: str,
                 output_data_name: str):
        super().__init__(self.get_tasks, self.task_handler, [])
        self.input_data_name = input_data_name
        self.output_data_name = output_data_name

    def get_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass


class ControllerFactory(Factory):
    def __init__(self, output_data_name: str):
        super().__init__(self.get_tasks, self.task_handler, [])
        self.output_data_name = output_data_name

    def get_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass
