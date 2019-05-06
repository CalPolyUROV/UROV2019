""" Sockets server for use in topside UI
"""
# System imports
from typing import Tuple


ServerTuple = Tuple[str, int]


class SocketsConfig:
    def __init__(self,
                 server_tuple: ServerTuple,
                 required: bool):
        self.server_tuple = server_tuple
        self.required = required
