from snr.profiler import Profiler
from typing import Union, List

from snr.debug import Debugger
from settings import Settings


class Context:

    def __init__(self,
                 name: str,
                 parent_context,
                 debugger: Debugger = None,
                 profiler: Profiler = None,
                 settings: Settings = None):
        self.name = name
        self.debugger = debugger
        self.profiler = profiler
        self.settings = settings
        if parent_context:
            self.parent_name = parent_context.name
            self.debugger = parent_context.debugger
            self.profiler = profiler
            self.settings = parent_context.settings
        elif (not self.debugger) or (not self.settings):
            print(f"FATAL: Incorrectly constructed context: {name}")

        self.info_channel = self.name + "_info"
        self.dbg_channel = self.name + "_verbose"
        self.log_channel = self.name
        self.warning_channel = self.name + "_warning"
        self.error_channel = self.name + "_error"
        self.critical_channel = self.name + "_critical"
        self.fatal_channel = self.name + "_fatal"

    def terminate(self):
        self.debugger.join()

    def err(self, *args: Union[list,  str]):
        self.debugger.debug(self.error_channel, *args)

    def warn(self, *args: Union[list,  str]):
        self.debugger.debug(self.warning_channel, *args)

    def log(self, *args: Union[list,  str]):
        self.debugger.debug(self.log_channel, *args)

    def dbg(self, *args: Union[list,  str]):
        self.debugger.debug(self.dbg_channel, *args)

    def info(self, *args: Union[list,  str]):
        self.debugger.debug(self.info_channel, *args)


def root_context() -> Context:
    settings = Settings()
    debugger = Debugger(settings)
    return Context("framework_main",
                   None,
                   debugger=debugger,
                   profiler=Profiler(debugger, settings),
                   settings=settings)
