
from typing import Callable, List, Tuple

from snr.dds.dds import DDS
from snr.dds.factory import DDSFactory
from snr.context import Context
from snr.endpoint_factory import EndpointFactory
from snr.factory import Factory
from snr.endpoint import Endpoint
from snr.task import SomeTasks, Task
from snr.task_queue import TaskQueue

TASK_TYPE_TERMINATE = "terminate"


class Node(Context):
    def __init__(self, parent_context: Context,
                 role: str, mode: str,
                 factories: List[Factory]):
        super().__init__(role + "_node", parent_context)
        self.role = role
        self.mode = mode
        dds_facs, endpoint_facs = self.seperate(factories)
        self.task_queue = TaskQueue(self, self.get_new_tasks)
        self.datastore = DDS(parent_context=self,
                             parent_node=self,
                             factories=dds_facs,
                             task_scheduler=self.task_queue.schedule)
        (self.endpoints, self.task_producers) = self.get_all(endpoint_facs)
        self.task_handlers = {
            TASK_TYPE_TERMINATE: self.terminate_task_handler
        }
        self.terminate_flag = False
        self.info("Initialized with {} endpoints",
                  [len(self.endpoints)])

    def loop(self):
        while not self.terminate_flag:
            t = self.task_queue.get_next()
            self.execute_task(t)
            self.sleep(self.settings.NODE_SLEEP_TIME)
        self.terminate()

    def get_new_tasks(self):
        """Retrieve tasks from endpoints and queue them.
        """
        new_tasks = []
        for task_source in self.task_producers:
            t = task_source()
            if t:
                if isinstance(t, Task):
                    new_tasks.append(t)
                elif isinstance(t, List):
                    new_tasks.extend(t)
                self.dbg("Produced task: {} from {}",
                         [t, task_source.__module__])
        return new_tasks

    def execute_task(self, t: Task):
        """Execute the given task

        Note that the task is passed in and can be provided on the fly rather
        than needing to be in the queue.
        """
        if not t:
            self.dbg("execute_task", "Tried to execute None")
            return

        task_result: List[Task] = []

        handler = self.task_handlers.get(t.task_type)
        if handler:
            result = self.profiler.time(f"{t.task_type}:{self.name}",
                                        lambda: handler(t))
            if result:
                task_result.append(result)
            # TODO: Time Node task handlers
            # TODO: Store all task handlers in Node

        for e in self.endpoints:
            handler = e.task_handlers.get(t.task_type)
            result = None
            if handler:
                if self.profiler is None:
                    result = handler(t)
                else:
                    result = self.profiler.time(f"{t.task_type}:{e.name}",
                                                lambda: handler(t))
            if result:
                task_result.append(result)

        self.dbg("Task execution resulted in {} new tasks",
                 [len(task_result)])
        if task_result:
            # Only procede if not empty
            self.schedule_task(task_result)

    def terminate_task_handler(self, t: Task) -> SomeTasks:
        if "node" in t.val_list:
            self.set_terminate_flag("terminate task")
        return None

    def set_terminate_flag(self, reason: str):
        self.info("Exit reason: {}", [reason])
        self.datastore.store("node_exit_reason", reason)
        self.terminate_flag = True
        for e in self.endpoints:
            e.set_terminate_flag()

    def terminate(self):
        """Execute actions needed to deconstruct a Node.
        Terminate is executed the main thread or process of an object.
        Conversely, join may be called from an external context such as
        another thread or process.
        """
        reason = self.datastore.get("node_exit_reason")

        # Shutdown all endpoints
        for e in self.endpoints:
            e.join()

        self.info("Terminated all endpoints")

        # Display everything that was stored in the datastore
        self.datastore.dump()
        # Shutdown the datastore
        self.datastore.join()

        # Display all information gathered by the profiler
        if self.profiler:
            self.profiler.join()
            self.profiler.dump()
        self.info("Node {} finished terminating", [self.role])

    def seperate(self, factories: List[Factory]
                 ) -> Tuple[List[DDSFactory],
                            List[EndpointFactory]]:
        dds_facs = []
        endpoint_facs = []
        self.info("Seperating facs: {}", [factories])
        for f in factories:
            if isinstance(f, DDSFactory):
                dds_facs.append(f)
            if isinstance(f, EndpointFactory):
                endpoint_facs.append(f)
        self.dbg("DDS facs: {}\n\t\t\tEndpoint facs: {}",
                 [dds_facs, endpoint_facs])
        return dds_facs, endpoint_facs

    def get_all(self,
                factories: List
                ) -> Tuple[List[Endpoint], List[Callable]]:
        self.info("Adding components from {} factories", [len(factories)])
        endpoints = []
        task_producers = []
        for factory in factories:
            endpoint = factory.get(self)
            if endpoint:
                endpoints.append(endpoint)
                task_producers.extend(endpoint.task_producers)
                self.info("framework_verbose",
                          "{} added {}", [factory, endpoint])
        return endpoints, task_producers

    def store_data(self, key: str, data):
        self.datastore.store(key, data)

    def get_data(self, key: str):
        return self.datastore.get(key)

    def use_data(self, key: str):
        return self.datastore.use(key)
