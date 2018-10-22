"""Test code for surface unit focusing on sockets
"""

# Our imports
import settings
from sockets_server import SocketsServer

settings.ROLE = "server"

s = SocketsServer("localhost", 9120)
s.open_server()
