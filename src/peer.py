from secrets import token_bytes
from src.torrent import Torrent
import asyncio

class peer:
    def __init__(self, port):
        self.port = port # 6881-6889