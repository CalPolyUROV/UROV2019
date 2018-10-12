"""Test code for surface unit focusing on sockets
"""

# Our imports
from sockets_server import SocketsServer

s = SocketsServer("localhost", 9120)
s.open_server()
