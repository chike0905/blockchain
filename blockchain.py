# -*- coding: utf-8 -*-
import json
import sys
import hashlib
import binascii
import logging

import random

# logging
logger = logging.getLogger("blcokchainlog")
logger.setLevel(10)
fh = logging.FileHandler('logger.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh.setFormatter(formatter)


peers = []
txpool = {}

class Blockchain:
    def __init__(self):
        # Make blockchain include genesis
        self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
        self.chain = [self.genesis]

    def generate_block(self,txobj):
        # Make new Block include all tx in txpool
        pool = []
        for txid in txobj.txpool.keys():
            pool.append(txobj.txpool[txid])
        blocknum = len(self.chain)
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        block = {"blocknum":blocknum, "tx":pool, "previous_hash":previoushash}
        txobj.txpool = {}
        print("-----------------------")
        print(json.dumps(block,indent=4,
                        ensure_ascii=False,
                        sort_keys=True))
        print("-----------------------")
        sblock = json.dumps(block)
        return block

    def add_new_block(self, block):
        # if pass verify block, add block to chain
        res = self.verify_block(block)
        if res["code"] == 0:
            self.chain.append(block)
            return True
        else:
            # TODO: resolv confrict of chain -> difine consensus
            return False

    def verify_block(self, block):
        # Verify Block
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["previous_hash"] == previoushash:
            msg = {"result":"block has been verified","code":0}
        else:
            # TODO: How different my chain and chain from block
            print("Previous blockhash in recive block is different to my last block hash")
            if self.chain[-1]["blocknum"] > block["blocknum"]:
                msg = {"result":"Send block is old","code":1}
            elif self.chain[-1]["blocknum"] < block["blocknum"]:
                msg = {"result":"Send block is orphan","code":2}
            else:
                msg = {"result":"Send block is from different chain","code":3}
        return msg