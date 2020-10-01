from typing import Tuple


class SocketsConfig:
    def __init__(self,
                 ip: str,
                 port: int):
        self.ip = ip
        self.port = port

    def tuple(self) -> Tuple[str, int]:
        return self.ip, self.port
