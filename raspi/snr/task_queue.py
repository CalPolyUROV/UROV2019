
from multiprocessing import Queue as Queue
from typing import Callable, Union

from snr.task import SomeTasks, Task
from snr.context import Context


class TaskQueue(Context):
    def __init__(self,
                 parent_context: Context,
                 task_source: Callable):
        super().__init__("task_queue", parent_context)
        self.get_new_tasks = task_source
        self.queue = Queue()

    def has_tasks(self) -> bool:
        """Report whether there are enough tasks left in the queue
        """
        return not self.queue.empty()

    def schedule(self, t: SomeTasks):
        """ Adds a Task or a list of Tasks to the node's queue
        """
        # t is None or empty list
        if not t:
            if t is None:
                self.warn("Cannot schedule None")
            elif isinstance(t, list):
                self.warn("Cannot schedule empty list")
            return

        # t is list
        if isinstance(t, list):
            # Recursively handle lists
            self.dbg("Recursively scheduling list of {} tasks",
                     [len(t)])
            for item in t:
                self.dbg("Recursively scheduling item {}",
                         [item])
                self.schedule_task(item)
            return

        # t is anything other than a task
        if not isinstance(t, Task):
            self.warn("Cannot schedule {} object {}", [type(t), t])
            return

        # Handle normal tasks
        self.dbg("Scheduling task {}", [t])
        # Ignore Priority
        self.queue.put(t)
        # TODO: Use priority with multiprocessing queue
        # if t.priority == TaskPriority.high:
        #     self.queue.put(t)  # High priotity at front (right)
        # elif t.priority == TaskPriority.normal:
        #     self.queue.put(t)  # Normal priotity at end (left)
        #     # TODO:  insert normal priority in between high and low
        # elif t.priority == TaskPriority.low:
        #     self.queue.put(t)  # Normal priotity at end (left)
        # else:
        #     self.dbg("schedule", "Cannot schedule task with priority: {}",
        #              [t.priority])

    def get_next(self) -> Union[Task, None]:
        """Take the next task off the queue
        """
        while not self.has_tasks():
            self.info("Ran out of tasks, getting more")
            self.get_new_tasks()
        return self.queue.get()
