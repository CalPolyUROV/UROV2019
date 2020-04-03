# Injection
from multiprocessing import Queue as Queue
from typing import List, Union

import settings
from snr.dds.dds import DDS
from snr.dds_factory import DDSFactory
from snr.debug import Debugger
from snr.discovery_server import DiscoveryServer
from snr.discovery_client import DiscoveryClient
from snr.endpoint_factory import EndpointFactory
from snr.factory import Factory
from snr.profiler import Profiler, Timer
from snr.task import SomeTasks, Task, TaskPriority
from snr.utils.utils import sleep

SLEEP_TIME = 0.015


class Node:
    def __init__(self, debugger: Debugger,
                 role: str, mode: str,
                 factories: List[Factory]):
        self.dbg = debugger.debug
        self.role = role
        self.name = f"{self.role}_node"
        self.mode = mode
        self.task_queue = Queue()
        self.terminate_flag = False  # Whether to exit main loop

        self.profiler = None
        if settings.ENABLE_PROFILING:
            self.profiler = Profiler(self.dbg)

        self.local_ip = None
        self.discovery_server = DiscoveryServer(self,
                                                settings.DISCOVERY_SERVER_PORT)

        dds_facs, endpoint_facs = self.seperate_components(factories)

        self.datastore = DDS(parent_node=self,
                             debug=self.dbg,
                             factories=dds_facs,
                             task_scheduler=self.schedule_task)
        self.store_node_ip()

        self.endpoints = []
        self.task_producers = []
        self.task_handlers = {
            "terminate": self.terminate_task_handler
        }

        self.add_endpoints(endpoint_facs)
        self.dbg("framework",
                 "Initialized with  {} endpoints",
                 [len(self.endpoints)])

    def add_endpoints(self, factories: List):
        self.dbg("framework_verbose", "Adding {} components", [len(factories)])
        for f in factories:
            endpoint = f.get(self)
            if endpoint is not None:
                self.endpoints.append(endpoint)
                if endpoint.task_producers:
                    for fn in endpoint.task_producers:
                        self.task_producers.append(fn)

            self.dbg("framework_verbose", "{} added {}", [f, endpoint])

    def store_node_ip(self):
        ip = self.get_local_ip()
        self.dbg("node", "Assigned {} node ip: {}", [self.role, ip])
        self.datastore.store("node_ip_address", ip)

    # TODO: Remove Sockets IP settings from Node
    def get_local_ip(self) -> str:
        if not self.local_ip:
            dc = DiscoveryClient(self.dbg)
            self.local_ip = dc.find_me(self.name, settings.SOCKETS_HOSTS)
        return self.local_ip
        # Panic
        self.dbg("node_error",
                 "Counld not ping to select IP, defaulting to {}",
                 [settings.DEBUG_IP])
        return settings.DEBUG_IP

        # # Old method for selecting IP
        # if self.mode == "debug":
        #     return "localhost"
        # else:
        #     if self.role == "robot":
        #         return settings.ROBOT_IP
        #     elif self.role == "topside":
        #         return settings.TOPSIDE_IP
        #     else:
        #         # Panic
        #         self.dbg("node_error",
        #                  "Node role {} not recognized. Counld not select IP",
        #                  [self.role])
        #         return settings.DEBUG_IP

    def get_remote_ip(self) -> str:
        if self.mode == "debug":
            return settings.DEBUG_IP
        else:
            if self.role == "robot":
                return settings.TOPSIDE_IP
            if self.role == "topside":
                return settings.ROBOT_IP
            # Panic
            self.dbg("node_error",
                     "Node role {} not recognized. Counld not get remote IP",
                     [self.role])
            return "localhost"

    def loop(self):
        while not self.terminate_flag:
            self.step_task()
            sleep(SLEEP_TIME)
        self.terminate()

    def get_new_tasks(self):
        """Retrieve tasks from endpoints and queue them.
        """
        # new_tasks = [e.get_new_tasks() for e in self.endpoints]
        for task_producer in self.task_producers:
            t = task_producer()
            if t and (isinstance(t, Task) or
                      (isinstance(t, List) and
                       len(t) > 0)):
                self.dbg("schedule_new_tasks",
                         "Produced task: {} from {}",
                         [t, task_producer.__module__])
                self.schedule_task(t)

    def execute_task(self, t: Task):
        """Execute the given task

        Note that the task is pass in and can be provided on the fly rather
        than needing to be in the queue.
        """
        if not t:
            self.dbg("execute_task", "Tried to execute None")
            return

        task_result = []

        handler = self.task_handlers.get(t.task_type)
        if handler is not None:
            result = handler(t)
            if result:
                task_result.append()
            # TODO: Time Node task handlers
            # TODO: Store all task handlers in Node

        for e in self.endpoints:
            handler = e.task_handlers.get(t.task_type)
            result = None
            if handler is not None:
                if self.profiler is None:
                    result = handler(t)
                else:
                    result = self.profiler.time(f"{t.task_type}:{e.name}",
                                                lambda: handler(t))
            if result:
                task_result.append(result)

        self.dbg("schedule_verbose",
                 "Task execution resulted in {} new tasks",
                 [len(list(task_result))])
        if task_result:
            # Only procede if not empty
            self.schedule_task(task_result)

    def terminate_task_handler(self, t: Task) -> SomeTasks:
        if "node" in t.val_list:
            self.set_terminate_flag("terminate task")
        return None

    def set_terminate_flag(self, reason: str):
        self.dbg("node_exit", "reason: {}", [reason])
        self.datastore.store("node_exit_reason", reason)
        self.terminate_flag = True

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

        self.dbg("framework", "Terminated all endpoints")

        # Display everything that was stored in the datastore
        self.datastore.dump()
        # Shutdown the datastore
        self.datastore.join()

        # Display all information gathered by the profiler
        if self.profiler is not None:
            self.profiler.join()
            self.profiler.dump()
        self.dbg("framework",
                 "Node {} finished terminating",
                 [self.role])

    def step_task(self):
        # Get the next task to execute
        t = self.get_next_task()
        self.execute_task(t)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return not self.task_queue.empty()

    def schedule_task(self, t: SomeTasks):
        """ Adds a Task or a list of Tasks to the node's queue
        """
        # t is None or empty list
        if not t:
            if t is None:
                self.dbg("schedule_warning", "Cannot schedule None")
            elif isinstance(t, list):
                self.dbg("schedule_warning", "Cannot schedule empty list")
            return

        # t is list
        if isinstance(t, list):
            # Recursively handle lists
            self.dbg("schedule_verbose",
                     "Recursively scheduling list of {} tasks",
                     [len(t)])
            for item in t:
                self.dbg("schedule_verbose",
                         "Recursively scheduling item {}",
                         [item])
                self.schedule_task(item)
            return

        # t is anything other than a task
        if not isinstance(t, Task):
            self.dbg("schedule_warning",
                     "Cannot schedule {} object {}", [type(t), t])
            return

        # Handle normal tasks
        self.dbg("schedule_verbose", "Scheduling task {}", [t])
        # Ignore Priority
        self.task_queue.put(t)
        # TODO: Use priority with multiprocessing queue
        # if t.priority == TaskPriority.high:
        #     self.task_queue.put(t)  # High priotity at front (right)
        # elif t.priority == TaskPriority.normal:
        #     self.task_queue.put(t)  # Normal priotity at end (left)
        #     # TODO:  insert normal priority in between high and low
        # elif t.priority == TaskPriority.low:
        #     self.task_queue.put(t)  # Normal priotity at end (left)
        # else:
        #     self.dbg("schedule", "Cannot schedule task with priority: {}",
        #              [t.priority])

    def get_next_task(self) -> Union[Task, None]:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            self.dbg("schedule_event", "Ran out of tasks, getting more")
            self.get_new_tasks()
        return self.task_queue.get()

    def seperate_components(self, factories: List[Factory]) -> \
            (List[DDSFactory], List[EndpointFactory]):
        dds_facs = []
        endpoint_facs = []
        self.dbg("node_verbose", "Seperating facs: {}", [factories])
        for f in factories:
            if isinstance(f, DDSFactory):
                dds_facs.append(f)
            if isinstance(f, EndpointFactory):
                endpoint_facs.append(f)
        self.dbg("node_verbose",
                 "DDS facs: {}\n\tEndpoint facs: {}",
                 [dds_facs, endpoint_facs])
        return dds_facs, endpoint_facs

    def store_data(self, key: str, data):
        self.datastore.store(key, data)

    def get_data(self, key: str):
        return self.datastore.get(key)

    def use_data(self, key: str):
        return self.datastore.use(key)
