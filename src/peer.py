from src.torrent import Torrent
import asyncio


class peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port