from src.logger import log
from src.tracker import Tracker
from src.torrent import Torrent
from bitstring import BitArray

class Block:
    def __init__(self, idx, offset, data):
        self.piece_idx = idx
        self.offset = offset
        self.data = data


class Piece:
    def __init__(self, index, legnth, _hash):
        self.index =  index
        self.length = legnth
        self._hash = _hash
        self.num_blocks = 524288
        self.blocks = []
    
    def add_block(self, block):
        self.blocks.insert(block.offset, block)
        
