from queue import Empty
from threading import Thread
from time import sleep
from typing import Callable, List

# Injection of Queue type
from multiprocessing import Queue as Queue

import settings
from snr.dds.dds_connection import DDSConnection
from snr.dds.page import Page
from snr.debug import Debugger
from snr.task import Task, TaskPriority
from snr.utils.utils import no_op, get_all

context = "dds"

SLEEP_TIME = 0.001

JOIN_TIMEOUT = 0.5

# Whether created threads are daemons.
DAEMON_THREADS = False


class DDS:
    def __init__(self,
                 parent_node=None,
                 debug=no_op,
                 factories: List[DDSConnection] = [],
                 task_scheduler: Callable[[Task], None] = no_op):
        self.dbg = debug

        self.data_dict = {}
        self.inbound_que = Queue()
        self.outbound_que = Queue()
        self.dbg(context,
                 "Creating connections from {} factories: {}",
                 [len(factories), factories])
        self.connections = get_all(factories, parent_node, self)
        self.schedule_task = task_scheduler
        self.terminate_flag = False

        self.rx_consumer = Thread(target=lambda:
                                  self.__consumer(q=self.inbound_que,
                                                  action=self.__write,
                                                  sleep_time=SLEEP_TIME),
                                  daemon=DAEMON_THREADS)
        self.tx_consumer = Thread(target=lambda:
                                  self.__consumer(q=self.outbound_que,
                                                  action=self.__send,
                                                  sleep_time=SLEEP_TIME),
                                  daemon=DAEMON_THREADS)

        self.rx_consumer.start()
        self.tx_consumer.start()

        self.dbg("dds",
                 "Initialized with {} connections",
                 [len(self.connections)])

    def store(self, key: str, value):
        self.inbound_store(Page(key, value))
        self.outbound_que.put(Page(key, value))

    def get(self, key: str):
        if not self.inbound_que.empty():
            # Hope that queue gets emptied
            # TODO: correctly flush datastore queue
            sleep(4 * SLEEP_TIME)

        page = self.data_dict.get(key)
        if page:
            return page.data
        return None

    def inbound_store(self, page: Page):
        self.inbound_que.put(page)

    def dump(self):
        for k in self.data_dict.keys():
            self.dbg("datastore_dump", "k: {}\tv: {}",
                     [k, self.data_dict.get(k).data])

    def __write(self, page: Page):
        self.data_dict[page.key] = page
        self.schedule_task(Task(f"proc_{page.key}", TaskPriority.normal, []))

    def __send(self, page: Page):
        for connection in self.connections:
            try:
                connection.send(page)
            except Exception as _e:
                pass

    def __consumer(self, q: Queue, action: Callable, sleep_time: int):
        """A method to be run by a thread for consuming the contents of a
        queue asynchronously
        """
        # Loop
        while not self.terminate_flag:
            try:
                page = q.get_nowait()
                if page is not None:
                    action(page)
                    page = q.get_nowait()
            except Empty:
                pass
            sleep(sleep_time)

        # Remaining lines
        try:
            page = q.get_nowait()
            while page is not None:
                action(page)
                page = q.get()
        except Exception as e:
            print(f"{e}")
        return

    def set_terminate_flag(self, reason: str):
        self.terminate_flag = True
        self.dbg("DDS",
                 "Preparing to terminate DDS for {}",
                 [reason])

    def join(self):
        """Shutdown DDS threads
        """
        self.set_terminate_flag("join")

        # Join child threads
        self.rx_consumer.join(JOIN_TIMEOUT)
        self.tx_consumer.join(JOIN_TIMEOUT)
