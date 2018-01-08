# -*- coding: utf-8 -*-
import logging
import os
import json

from blockchain import Blockchain
from transaction import Transaction
from messaging import Messaging
from settings import *

import chord.dht

# For debug
from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed



class BlockchainService:
    def __init__(self, myaddr, myport="5555", inital_peer_addr=None, inital_peer_port="5555", rcv=True):
        # Make data dir
        if not os.path.isdir(".blockchain"):
            os.makedirs(".blockchain")
        self.logger = self.init_logger()
        self.logger.log(20,"Start Blockchain Service")
        self.tx = Transaction(self.logger)
        if STORAGE == "DHT":
            if inital_peer_addr:
                self.dht = chord.dht.DHT(self.logger, chord.dht.Address(myaddr, myport), chord.dht.Address(inital_peer_addr, inital_peer_port))
                self.bc = Blockchain(self.logger, self.tx, self.dht)
                self.msg = Messaging(myaddr, myport, self.logger, self.bc, self.tx, self.dht)
                self.msg.add_peer(inital_peer_addr, inital_peer_port)
            else:
                self.dht = chord.dht.DHT(self.logger, chord.dht.Address(myaddr, myport))
                self.bc = Blockchain(self.logger, self.tx, self.dht)
                self.msg = Messaging(self.logger, self.bc, self.tx, self.dht)
        elif STORAGE == "local":
            if inital_peer_addr:
                self.bc = Blockchain(self.logger, self.tx)
                self.msg = Messaging(myaddr, myport, self.logger, self.bc, self.tx)
                self.msg.add_peer(inital_peer_addr, inital_peer_port)
            else:
                self.bc = Blockchain(self.logger, self.tx)
                self.msg = Messaging(myaddr, myport, self.logger, self.bc, self.tx)

        if rcv:
            self.msg.start_rcv(myaddr, myport)

    def init_logger(self):
        # logging
        logger = logging.getLogger("blcokchainlog")
        logger.setLevel(10)
        fh = logging.FileHandler('.blockchain/logger.log')
        logger.addHandler(fh)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fh.setFormatter(formatter)
        return logger

    def make_block(self, score):
        # take score is for debug
        block = self.bc.generate_block(score)
        res, code = self.bc.add_new_block(block)
        if not res:
            print("Block is not generated")
        else:
            print("Block is generated")
            # send generated block
            blkmsg = {"type":"block", "body":block}
            for peer in self.msg.peers:
                self.msg.send(blkmsg, peer)

    def make_tx(self):
        transaction = self.tx.generate_tx()
        if not self.tx.add_tx_pool(transaction):
            print("Transaction is not generated")
        else:
            print("Transaction is generated")
            # send generated block
            txmsg = {"type":"tx", "body":transaction}
            for peer in self.msg.peers:
                self.msg.send(txmsg, peer)

    def shutdown(self):
        self.dht.shutdown()

if __name__ == '__main__':
    embed()
