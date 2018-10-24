from task import Task
from task import TaskType
from task import TaskPriority
from task import decode

t1: Task = Task(TaskType.debug_str, TaskPriority.normal, ["text", 1, 2, "3"])
data: bytes = t1.encode()
t2: Task = decode(data)

assert(t1 == t2)
