# -*- coding: utf-8 -*-
import logging

from blockchain import Blockchain
from transaction import Transaction
from messaging import Messaging

# For debug
from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed


# logging
logger = logging.getLogger("blcokchainlog")
logger.setLevel(10)
fh = logging.FileHandler('logger.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh.setFormatter(formatter)

class BlockchainService:
    def __init__(self):
        self.tx = Transaction()
        self.bc = Blockchain(transaction)
        self.msg = Messaging(blockchain, transaction)

    def make_block(self):
        block = self.bc.generate_block()
        if not self.bc.add_new_block(block):
            print("Block is not generated")
        else:
            print("Block is generated")
            # send generated block
            blkmsg = {"type":"block", "body":block}
            for peer in self.msg.peers:
                self.msg.send(peer, blkmsg)


embed()
