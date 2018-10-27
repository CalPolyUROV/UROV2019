"""Test code for surface unit focusing on sockets
"""

# Our imports
import settings
from debug import debug
from debug import debug_f
from task import Task
from task import TaskType
from task import TaskPriority
from sockets_server import SocketsServer
from server import handle_response

settings.ROLE = "server"

s = SocketsServer(settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)

s.open_server()

task_queue = []
handler = handle_response

while 1:
    s.accept_connection()
    while 1:
        s.recieve_data(task_queue, handler)

    s.conn.close()
    s.close()
