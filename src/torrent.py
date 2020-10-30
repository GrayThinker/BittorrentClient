import bencoder
import sys
import pprint
import hashlib


class Torrent:
    """
    Represents the torrent extraceted from the .torrent file
    """
    def __init__(self, file_path):
        self.path = file_path

    @property
    def metainfo(self):
        return self.read_torrent(self.path)

    @property
    def data(self):
        return self.metainfo[b"info"]
    
    @property
    def info(self):
        return self.metainfo[b"info"]

    @property
    def info_hash(self):
        return hashlib.sha1(bencoder.encode(self.data)).digest()

    @property
    def length(self):
        size = 0
        if not self.files:
            return self.data[b"length"]

        for file in self.files:
            size += file["length"]
        return size

    @property
    def files(self):
        files = []
        try:
            raw_files = self.data[b"files"]
        except KeyError:
            return {}

        for raw_file in raw_files:
            f = dict()
            f["length"] = raw_file[b"length"]
            f["path"] = raw_file[b"path"][0].decode("utf-8")
            files.append(f)
        return files
    
    @property
    def announce(self):
        return self.metainfo[b"announce"].decode("utf-8")

    @property
    def announce_list(self):
        announce_list = []
        raw_announce_list =  self.metainfo[b"announce-list"]
        for item in raw_announce_list:
            announce_list.append(item[0].decode("utf-8"))
        return announce_list

    @property
    def piece_len(self):
        return self.data[b"piece length"]

    @property
    def name(self):
        return self.data[b"name"]

    @property
    def pieces(self):
        return self.data[b"pieces"]

    def read_torrent(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                return bencoder.decode(file.read())
        except FileNotFoundError:
            print("Error file not found\n")
            sys.exit(1)

    def __repr__(self):
        return pprint.pformat(self.metainfo)
