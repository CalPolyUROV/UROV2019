from threading import Thread
import socket
import json

LOCALHOST = "localhost"
DAEMON_THREAD = True
MAX_CONNECTIONS = 10

context = "discovery_server"


class DiscoveryServer:
    def __init__(self, parent_node, port: int):
        self.parent_node = parent_node
        self.dbg = parent_node.dbg
        self.host_tuple = (LOCALHOST, port)
        self.s = None

        self.__init_socket()

        self.thread = Thread(target=self.loop,
                             args=[],
                             daemon=DAEMON_THREAD)
        self.thread.start()

    def __init_socket(self):
        if self.s is not None:
            self.__close()

        # Create socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.s.settimeout(settings.SOCKETS_SERVER_TIMEOUT)

        # Bind to the socket
        try:
            self.s.bind(self.host_tuple)
            self.dbg(context + "_event",
                     "Socket bound to {}:{}",
                     [self.host_tuple[0], self.host_tuple[1]])
        except socket.error as socket_error:
            self.dbg(context + "_critical",
                     "Bind failed: {}", [socket_error])
            self.s.close()
            # sleep(settings.SOCKETS_RETRY_WAIT)
        # Listen for connections
        try:
            self.s.listen(MAX_CONNECTIONS)
            self.dbg(context + "_event",
                     "Server now listening")
        except Exception as error:
            self.dbg(context + "_error",
                     "Error listening: {}",
                     [error.__repr__()])
            self.s.close()
            return

    def loop(self):
        while True:
            self.__handle_connection()

    def __handle_connection(self):
        # Create connection to the client
        try:
            # Blocking call waiting for the client to connect
            self.dbg(context + "_event",
                     "Blocking on accept_connection for {}",
                     [context])
            conn, addr = self.s.accept()
            encoded_data = self.parent_node.name.encode()
            self.dbg(context + "_verbose",
                     "Providing name: {} to {}",
                     [encoded_data, addr])
            conn.sendall(encoded_data)
            conn.close()
            return
        except (socket.timeout, OSError, Exception) as e:
            if isinstance(e, socket.timeout):
                self.dbg(context,
                         "Restarting sockets server after idle timeout")
            else:
                self.dbg(context,
                         "Connection failed: {}", [e])
