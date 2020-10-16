import bencoder
import sys
import pprint
import hashlib


class Torrent:
    def __init__(self, file_path):
        self.path = file_path
        self.metainfo = self.read_torrent(file_path)
        self.data = self.metainfo[b"info"]
        self.info_hash = hashlib.sha1(bencoder.encode(self.data)).digest()

    def read_torrent(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                return bencoder.decode(file.read())
        except FileNotFoundError:
            print("Error file not found\n")
            sys.exit(1)

    def __repr__(self):
        return pprint.pformat(self.metainfo)
        # return f"{self.data.keys()}\n{self.info.keys()}\n"

tor = Torrent(".\\tests\\big-buck-bunny.torrent")
print(tor.info_hash)