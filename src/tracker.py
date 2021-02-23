from urllib.parse import urlencode
from src.torrent import Torrent
from secrets import token_bytes
from src.logger import log
from struct import unpack
import ipaddress
import bencoder
import asyncio
import aiohttp
import sys

class Tracker:
    """Connection to a tracker for the torrent"""
    def __init__(self, torrent):
        try:
            assert isinstance(torrent, Torrent)
        except:
            log.critical("Tracker received non Torrent object")
            raise TypeError()

        self._peers = []
        self.torrent = torrent
        self.PEER_ID = token_bytes(10).hex()
        self.session = aiohttp.ClientSession()
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

    @property
    async def peers(self):
        """
        Using this because __init__() cannot use async/await
        """
        if not self._peers:
            self._peers = await self.get_peers()
        return self._peers

    async def get_online_announce(self):
        trackers = await self.find_online_tracker()
        try:
            # discard after each subsequent call
            self.announce = str(trackers.pop())
        except IndexError:
            log.error("No online trackers found\n")
            raise IndexError
            

    async def close(self):
        await self.session.close()
        log.info("Closed session")

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
                log.info("Found online tracker")
                return working

    async def get_peers(self):
        """
        query tracker for peers with torrent pieces
        """
        await self.get_online_announce()
        self.url = self.announce + '?' + urlencode(self.params)
        response = await self.session.get(self.url)
        if response.status != 200:
            log.warning("Couldn't get peers from tracker")
            # TODO: get different tracker from find_online;
            await self.session.close()
            raise ConnectionError
        response_data = await response.read()
        res = bencoder.decode(response_data)
        log.info("got peers")
        return self.parse_peers(res[b"peers"])

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
        log.info("parsed peers")
        return peers