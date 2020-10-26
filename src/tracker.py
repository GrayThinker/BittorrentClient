from src.torrent import Torrent
from secrets import token_bytes
import asyncio
import aiohttp
from urllib.parse import urlencode

class Tracker:
    """Connection to a tracker for the torrent"""
    def __init__(self, torrent):
        try:
            assert isinstance(torrent, Torrent)
        except:
            raise TypeError()

        self.torrent = torrent
        self.url = str(torrent.announce)
        self.PEER_ID = token_bytes(10).hex()
        self.peers = []
        self.params = {
            'info_hash' : self.torrent.info_hash,
            'peer_id' : self.PEER_ID,
            'no_peer_id' : 0,
            'event' : 'started',
            'port' : 6882,
            'uploaded' : 0,
            'downloaded' : 0,
            'left' : self.torrent.length,
            'compact' : 1
        }
    
    async def get_peers(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(self.url, params=self.params)
            data = await response.read()
            print(data)

tor = Torrent(".\\tests\\wired-cd.torrent")
t = Tracker(tor)
loop = asyncio.get_event_loop()
loop.run_until_complete(t.get_peers())