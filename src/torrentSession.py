"""
    A class to keep track of the torrent file, tracker, peers, peer_id
    all variables needed by peer, tracker, etc.
"""
from src.torrent import Torrent
from src.tracker import Tracker


class TorrentSession:
    def __init__(self, file):
        self.torrent = Torrent(file)
        self.tracker = Tracker(self.torrent)
        self.PEER_ID = self.tracker.PEER_ID
        self.info_hash = self.torrent.info_hash
    
