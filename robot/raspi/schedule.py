""" Scheduling class for queue based scheduling in Node class
"""

# Our imports
import settings
from utils import debug, debug_f
from task import Task, TaskPriority, TaskType


class Schedule:
    def __init__(self, initial_tasks: list, handler, task_source):
        self.task_list = initial_tasks
        # self.task_index = 0
        self.handler = handler
        self.task_source = task_source

    def schedule_task(self, input: Task or list):
        if isinstance(input, list):
            for t in input:
                self.schedule_task(t)
        elif not isinstance(input, Task):
            debug_f("schedule", "Cannot schedule non task object {}", [input])
            return
        debug_f("schedule", "Scheduling task {}", [input])

        if input.priority == TaskPriority.high:
            self.task_list.insert(0, input)
        elif input.priority == TaskPriority.normal:
            self.task_list.append(input)
            # TODO: intelligently insert normal priority tasks after any high priority tasks, but before low priority tasks
        elif input.priority == TaskPriority.low:
            self.task_list.append(input)
        else:
            debug_f(
                "schedule", "Cannot schedule task with unknown priority: {}", [input.priority])
        # self.task_index += 1

    def execute_task(self, t: Task):
        if t == None:
            debug("execute_task", "Tried to execute None")
            return
        # TODO: Send commands to Teensy (In final commands will come from sockets connection OR event loop will get updated values in an RTOS manner)
        # TODO: Write logic choosing a command to send (maybe use a queue)
        sched_list = self.handler(t)
        if not (sched_list == None):
            for t in sched_list:
                self.schedule_task(t)

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return 0 < len(self.task_list)

    def get_new_tasks(self) -> bool:
        sched_list = self.task_source()
        self.schedule_task(sched_list)

    def get_next_task(self) -> Task or None:
        """Take the next task off the queue
        """
        if not self.has_tasks():
            if not self.get_new_tasks():
                return None

        return self.task_list.pop(0)


class Node:
    def __init__(self):
        raise NotImplementedError(
            "Subclass of Node does not implement __init__()")

    def loop(self):
        raise NotImplementedError("Subclass of Node does not implement loop()")

    def terminate(self):
        raise NotImplementedError(
            "Subclass of Node does not implement terminate()")
