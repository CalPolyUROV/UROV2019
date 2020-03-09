from ctypes import cdll, CDLL, c_ubyte, c_uint

import settings
from snr.endpoint import Endpoint
from snr.task import SomeTasks, Task
from snr.node import Node
from snr.utils import debug


class Zybo(Endpoint):
    def __init__(self, parent: Node, name: str,
                 input: str, output: str):
        super().__init__(parent, name)
        self.task_handlers = {
            "serial_com": self.handle_serial_com
        }
        if not settings.SIMULATE_PWM:
            # https://docs.python.org/3/library/ctypes.html
            pwm_lib_name = "/home/ubuntu/urov/raspi/snr/zynq/pwm/so/libpwmuio.so"
            # cdll.LoadLibrary(pwm_lib_name)
            self.pwm_lib = CDLL(pwm_lib_name)
            self.pwm_lib.initDemo()

        if not settings.SIMULATE_DMA:
            dma_lib_name = "/home/ubuntu/urov/raspi/snr/zynq/dma-proxy/dma-proxy-test.so"
            # cdll.LoadLibrary(dma_lib_name)
            self.dma_lib = CDLL(dma_lib_name)
            # self.dma_lib.initDemo()
        else:
            debug("dma_verbose",
                  "Simulating DMA only. C library not loaded.")

        self.input = input
        self.output = output

    def get_new_tasks(self) -> SomeTasks:
        # TODO: Match serial task generation
        return None

    def handle_serial_com(self, t: Task) -> SomeTasks:
        sched_list = []
        debug("serial_verbose",
              "Executing serial com task: {}", [t.val_list])
        cmd = t.val_list[0]
        reg = t.val_list[1]
        if len(t.val_list) > 2:
            val = t.val_list[2]
        else:
            val = 0

        self.dma_transact()
        result = self.pwm_write(cmd, reg, val)

        # result = self.send_receive(t.val_list[0],
        #                            t.val_list[1::])
        if result is None:
            # debug("zybo_verbose",
            #       "Received no data in response from serial message")
            pass
        elif isinstance(result, Task):
            sched_list.append(result)
        elif isinstance(result, list):
            for new_task in list(result):
                sched_list.append(new_task)

        return sched_list

    def dma_transact(self):
        s = "Hello, Sukhman!__"
        if not settings.SIMULATE_DMA:   
            self.dma_lib.test(bytes(s, "ASCII"), len(s))
        else:
            debug("dma_sim", 
                  "Simulating DMA transaction with msg: \"{}\"",
                  [s])

    def pwm_write(self, cmd: str, reg: int, val: int):
        speed = self.map_thrust_value(val)

        if not settings.SIMULATE_PWM:
            self.pwm_lib.writePWM(c_ubyte(reg), c_uint(speed))
            debug("pwm_verbose", "Writing PWM: cmd: {}, reg: {}, val: {}->{}",
                  [cmd, reg, val, speed])
        else:
            debug("pwm_sim", "Writing simualted PWM: cmd: {}, reg: {}, val: {}->{}",
                  [cmd, reg, val, speed])

    def map_thrust_value(self, val: int) -> int:
        # -100 to 0 to 100
        # add 1500
        # 1390us to 1500us to 1610us
        # 1us = 100 ticks
        if val > 100:
            return 255
        if val < -100:
            return 0
        speed = int(((val * 30) + 1500) * 10)
        debug("serial_packet",
              "Converted motor speed from {} to {}", [val, speed])
        return speed

    def terminate(self):
        if not settings.SIMULATE_DMA:
            pass
        if not settings.SIMULATE_PWM:
            # Deallocate C objects
            debug("pwm_verbose", "Freeing C objects...")
            self.pwm_lib.exitHandler()
            debug("pwm_verbose", "Freed C objects")
        else:
            debug("pwm_verbose", "Simulated c objects freed")
