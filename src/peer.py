from secrets import token_bytes
import asyncio

class peer:
    def __init__(self, port):
        self.peer_id = token_bytes(20)
        self.port = port # 6881-6889