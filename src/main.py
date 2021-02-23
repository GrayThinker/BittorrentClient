import argparse
import asyncio
import aiohttp
import logging
from src.logger import log
from src.torrent import Torrent
from src.tracker import Tracker
from src.peer import Peer

def get_args():
    parser = argparse.ArgumentParser(prog="pytor",
                                     description="Download a torrent"
                                     )
    parser.add_argument("-d", "--debug",
                        action="store_true"
                        )
    parser.add_argument("file", 
                        nargs="?",
                        default=".\\tests\\Justice League.torrent",
                        help="The .torrent file to download from")
    args = parser.parse_args()
    
    parser.add_argument("storeDir",
                        nargs="?",
                        help="Directory to store the download")

    parser.add_argument("-s", "--secret",
                        action="store_true",
                        help="use secret info for peers and tracker")

    parser.add_argument("-V", "--Verbose",
                        action="store_true",
                        help="show all loggin info")
    
    return parser.parse_args()

async def main():

    args = get_args()
    file = args.file
    
    if args.Verbose:
        log.setLevel(logging.DEBUG)

    if args.debug:
        log.setLevel(logging.INFO)
    
    else:
        log.setLevel(logging.ERROR)


#Testing
    torrent = Torrent(file)

    tracker = Tracker(torrent)
    peer_ids = await tracker.peers
    await tracker.close()
    peers = []
    for peer_id in peer_ids:
        peers.append(Peer(peer_id[0], peer_id[1], torrent.info_hash, tracker.PEER_ID))    
    working_peers = await asyncio.gather(*[test_peer(peer) for peer in peers])
    while True:
        try:
            working_peers.remove(None)
        except ValueError:
            break
    print(working_peers)
    
async def test_peer(peer):
    if await peer.connect():
        return peer
    return None

if __name__ == "__main__":
    asyncio.run(main())