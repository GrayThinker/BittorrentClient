from src.torrent import Torrent
from secrets import token_bytes
from urllib.parse import urlencode
from struct import unpack
import ipaddress
import bencoder
import asyncio
import aiohttp

class Tracker:
    """Connection to a tracker for the torrent"""
    def __init__(self, torrent):
        try:
            assert isinstance(torrent, Torrent)
        except:
            raise TypeError()

        self.torrent = torrent
        self.PEER_ID = token_bytes(10).hex()
        self.session = aiohttp.ClientSession()
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

    async def get_online_announce(self):
        self.announce = str((await self.find_online_tracker())[0])

    async def close(self):
        await self.session.close()

    async def test(self, announce):
        try:
            response = await asyncio.wait_for(self.session.get(announce), timeout=1.0)
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None
        return announce
    
    async def find_online_tracker(self):
        """
        query all the trackers in the announce list to find online trackers
        """
        working = await (asyncio.gather(*[self.test(announce) for announce in self.torrent.announce_list]))
        while True:
            try:
                working.remove(None)
            except ValueError:
                return working
    
    async def get_peers(self):
        """
        query tracker for peers with torrent pieces
        """
        await self.get_online_announce()
        self.url = self.announce + '?' + urlencode(self.params)
        response = await self.session.get(self.url)
        response_data = await response.read()
        res = bencoder.decode(response_data)
        self.peers = self.parse_peers(res[b"peers"])
        print("Parsed peers")

    def parse_peers(self, peers_bin):
        """
        parse raw (ipaddress, port) pairs to correct form
        """
        peers = []
        for i in range(0, len(peers_bin), 6):
            address = str(ipaddress.IPv4Address(peers_bin[i:i+4]))
            port = peers_bin[i+4:i+6]
            port = unpack(">H", port)[0]
            peers.append((address, port))
        return peers

async def main():
    tor = Torrent(".\\tests\\Justice League.torrent")
    t = Tracker(tor)
    await t.get_peers()
    await t.close()

    

if __name__ == "__main__":
    asyncio.run(main())