import asyncio

class DownloadManager:
    def __init__(self, torrent, peers):
        self.torrent = torrent
        self.peers = peers