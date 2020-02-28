from multiprocessing import JoinableQueue
from queue import Empty
from threading import Thread
from time import sleep
from typing import Callable, List

# Injection of Queue type
from multiprocessing import Queue as Queue

import settings
from snr.dds.page import Page
from snr.debug import Debugger
from snr.utils.utils import no_op

SLEEP_TIME = 0.001


def if_joinable(q: Queue, action: Callable):
    if isinstance(q, type(JoinableQueue)):
        action()


class DDSConnection:
    def send(self):
        raise NotImplementedError


class DDS:
    def __init__(self,
                 dbg: Debugger = None,
                 connections: List[DDSConnection] = [],
                 task_scheduler: Callable = no_op
                 ):
        self.dbg = dbg

        self.data_dict = {}
        self.inbound_que = Queue()
        self.outbound_que = Queue()
        self.connections = connections
        self.task_scheduler = task_scheduler

        self.terminate_flag = False

        self.rx_consumer = Thread(target=lambda:
                                  self.__consumer(self.inbound_que,
                                                  self.__write))
        self.tx_consumer = Thread(target=lambda:
                                  self.__consumer(self.outbound_que,
                                                  self.__send))

        self.rx_consumer.start()
        self.tx_consumer.start()

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
        print(f"Wrote: {page}")

    def __send(self, page: Page):
        for connection in self.connections:
            try:
                connection.send(page)
            except Exception as _e:
                pass
        print(f"Sent: {page}")

    def __consumer(self, q: Queue, action: Callable):
        """
        """
        # Loop
        while not self.terminate_flag:
            try:
                page = q.get_nowait()
                if page is not None:
                    action(page)
                    if_joinable(q, lambda: q.task_done())
                    page = q.get_nowait()
            except Empty:
                pass
            sleep(SLEEP_TIME)

        # Remaining lines
        try:
            page = q.get_nowait()
            while page is not None:
                action(page)
                if_joinable(q, q.task_done)
                page = q.get()
        except Exception as e:
            print(f"{e}")
        return

    def set_terminate_flag(self, reason: str):
        self.terminate_flag = True

    def terminate(self):
        self.dump()
        self.join()

    def join(self):
        """Shutdown DDS threads
        """
        self.terminate_flag = True

        # Join only joinable queues
        if_joinable(self.inbound_que, lambda: self.inbound_que.join())
        if_joinable(self.inbound_que, lambda: self.outbound_que.join())

        self.rx_consumer.join()
        self.tx_consumer.join()
