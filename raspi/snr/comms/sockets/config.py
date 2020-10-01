from typing import Tuple


class SocketsConfig:
    def __init__(self,
                 ip: str,
                 port: int,
                 required: bool
                 ):
        self.ip = ip
        self.port = port
        # self.required = required

    def tuple(self) -> Tuple[str, int]:
        return self.ip, self.port
