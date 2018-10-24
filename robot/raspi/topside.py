"""Test code for surface unit focusing on sockets
"""

# Our imports
import settings
from sockets_server import SocketsServer

settings.ROLE = "server"

s = SocketsServer(settings.TOPSIDE_IP_ADDRESS, settings.TOPSIDE_PORT)
s.open_server()
