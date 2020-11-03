from secrets import token_bytes
from src.tracker import Tracker
from src.torrent import Torrent
from struct import pack, unpack
from src.logger import log
import asyncio

PSTR = "BitTorrent protocol"
keepAlive = None
choke = 0
unChoke = 1
interested = 2
notInterested = 3
have = 4
bitField = 5
request = 6
piece = 7
cancel = 8
port = 9

class Peer:
    def __init__(self, ip, port, info_hash, peer_id):
        self._ip = ip
        self._port = port
        self.info_hash = info_hash
        self.peer_id = peer_id

        self._is_interested = 0
        self._is_choking = 1
        self._am_interested = 0
        self._am_choking = 1

    async def send_interested(self):
        assert self.writer
        msg = pack(">Ib", 1, 2) #use message class
        self.writer.write(msg)
        await self.writer.drain()

    def request_piece(self):
        pass

    def __repr__(self):
        return f"[{self._ip}:{self._port}]"

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def am_choking(self):
        return self._am_choking

    @property
    def am_interested(self):
        return self._am_interested

    @property
    def is_choking(self):
        return self._is_choking
        
    @property
    def is_interested(self):
        return self._is_interested
    
    @property
    def handshake(self):
        return pack(
            '>B19s8x20s20s',
            19,
            PSTR.encode(),
            self.info_hash,
            self.peer_id.encode("utf-8")
        )        

    async def connect(self):
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self._ip, self._port), timeout=5)
        except (asyncio.TimeoutError, OSError):
            log.info(f"Couldn't Connect to {self}")
            # print(f"Couldn't Connect to {self}") #log
            return False

        writer.write(self.handshake)
        await writer.drain()
        try:
            resp = await asyncio.wait_for(reader.read(68), timeout=5)
        except (asyncio.TimeoutError):
            log.info(f"{self} took too long to shake")
            return False
        if len(resp)!= 68:
            log.info(f"{self} returned invalid handshake")
            writer.close()
            await writer.wait_closed()
            return False
        
        hands = unpack('>B19s8x20s20s', resp)
        
        if hands[2] != self.info_hash:
            log.info(f"{self} gave non-matching info-hash")
            writer.close()
            await writer.wait_closed()
            return False
        
        self.peers_own_id = hands[3]
        self.reader = reader
        self.writer = writer
        log.info(f"connected to {self}")
        return True

    
    async def download(self):
        # loop
        if not self.is_interested:
            await self.send_interested()
        
        resp = await self.reader.read()
        msg = Message(resp)
        if msg.code == 0: #choke
            self._is_choking = 1

        elif msg.code == 1: # unchoke
            self._is_choking = 0

        elif msg.code == 2: # interested
            self._is_interested = 1
        
        elif msg.code == 3: # not interestted
            self._is_interested = 0
        
        elif msg.code == 4: # have
            piece_index = msg.index
        
        elif msg.code == 5: # bitfield
            pass
        elif msg.code == 6: # request
            pass
        elif msg.code == 7: # piece
            pass
        elif msg.code == 8: # cancel
            pass
        elif msg.code == 9: # port
            pass
        else: 
            pass

class Message:
    def __init__(self, raw_bytes):
        self.raw_bytes = raw_bytes
        self.length = unpack(">I", raw_bytes[:4])[0]
        if self.length == 0:
            self.code = keepAlive
        else:
            self.code = unpack(">b", raw_bytes[4:5])[0]
            if self.code == have:
                self.index = unpack(">I", raw_bytes[5:9])[0]
            elif self.code == bitField:
                self.bitField = raw_bytes[5:self.length+4]
            elif self.code == request:
                self.index, self.begin, self.length = unpack(">III", raw_bytes[5:self.length+4])
            elif self.code == piece:
                self.index, self.begin, self.block = unpack(f">II{self.length-9}s", raw_bytes[5:self.length+4])
            elif self.code == cancel:
                self.index, self.begin, self.length = unpack(">III", raw_bytes[5:self.length+4])
            elif self.code == port:
                self.listen_port = unpack(">h", raw_bytes[5:self.length+4])[0]
