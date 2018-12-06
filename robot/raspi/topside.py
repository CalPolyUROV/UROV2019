#!/usr/bin/python3
"""Test code for surface unit focusing on sockets
"""

# Our imports
import settings
from utils import exit, debug, debug_f
from task import Task, TaskType, TaskPriority
from sockets_server import SocketsServer
from control_unit import ControlUnit


def main():
    settings.ROLE = "server"
    # settings.PRINTING = False

    cu = ControlUnit()
    s = SocketsServer(settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)

    s.open_server()

    task_queue = []
    handler = cu.handle_response

    while 1:
        s.accept_connection()
        while 1:
            s.recieve_data(task_queue, handler)

        s.conn.close()
        s.close()


# https://stackoverflow.com/questions/21120947/catching-keyboardinterrupt-in-python-during-program-shutdown
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit("Interrupted, exiting")
