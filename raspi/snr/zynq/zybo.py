from ctypes import cdll, CDLL

import settings
from snr.endpoint import Endpoint
from snr.task import SomeTasks, Task
from snr.node import Node
from snr.utils import debug


class Zybo(Endpoint):
    def __init__(self, parent: Node, name: str,
                 input: str, output: str):
        super().__init__(parent, name)

        if not settings.SIMULATE_DMA:
            # https://docs.python.org/3/library/ctypes.html
            lib_name = "/home/ubuntu/urov2019/raspi/snr/zynq/pwm/so/libpwmuio.so"
            cdll.LoadLibrary(lib_name)
            self.pwm_lib = CDLL(lib_name)

        self.input = input
        self.output = output

    def get_new_tasks(self) -> SomeTasks:
        # TODO: Match serial task generation
        return None

    def task_handler(self, t: Task) -> SomeTasks:
        sched_list = []
        if t.task_type == "serial_com":
            debug("serial_verbose",
                  "Executing serial com task: {}", [t.val_list])
            cmd = t.val_list[0]
            reg = t.val_list[1]
            if len(t.val_list) > 2:
                val = t.val_list[2]
            else:
                val = 0

            result = self.dma_write(cmd, reg, val)

            # result = self.send_receive(t.val_list[0],
            #                            t.val_list[1::])
            if result is None:
                debug("robot",
                      "Received no data in response from serial message")
            elif isinstance(result, Task):
                sched_list.append(result)
            elif isinstance(result, list):
                for new_task in list(result):
                    sched_list.append(new_task)

        return sched_list

    def dma_write(self, cmd: str, reg: int, val: int):
        debug("dma_verbose", "Writing DMA: cmd: {}, reg: {}, val: {}",
              [cmd, reg, val])

        if not settings.SIMULATE_DMA:
            self.pwm_lib.run_demo()

       # debug("dma_verbose", "cmd returned: {}", [status])

    def terminate(self):
        if not settings.SIMULATE_DMA:
            pass
