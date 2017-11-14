# -*- coding: utf-8 -*-
import json
import hashlib

class Blockchain:
    def __init__(self, logger, txobj):
        # Make blockchain include genesis
        self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
        self.chain = [self.genesis]
        self.logger = logger
        self.tx = txobj

    def generate_block(self):
        # Make new Block include all tx in txpool
        pool = []
        for txid in self.tx.txpool.keys():
            pool.append(self.tx.txpool[txid])
        blocknum = len(self.chain)
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        block = {"blocknum":blocknum, "tx":pool, "previous_hash":previoushash}
        self.tx.txpool = {}

        print("-----------------------")
        print(json.dumps(block,indent=4,
                        ensure_ascii=False,
                        sort_keys=True))
        print("-----------------------")
        self.logger.log(20,"Generate New Block(%s)" % block["blocknum"])
        return block

    def add_new_block(self, block):
        # if pass verify block, add block to chain
        res = self.verify_block(block)
        if res["code"] == 0:
            for tx in block["tx"]:
                if tx["id"] in self.tx.txpool.keys():
                    self.tx.txpool.pop(tx["id"])
            self.chain.append(block)
            self.logger.log(20,"Append New Block(%s) to my chain" % block["blocknum"])
            return True
        else:
            # TODO: resolv confrict of chain -> difine consensus
            return res

    def verify_block(self, block):
        # Verify Block
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["previous_hash"] == previoushash:
            msg = {"result":"block has been verified","code":0}
        else:
            # TODO: How different my chain and chain from block
            self.logger.log(20,"Previous blockhash in check block is different from my last block hash")
            if self.chain[-1]["blocknum"] > block["blocknum"]:
                msg = {"result":"Send block is old","code":1}
            elif self.chain[-1]["blocknum"] < block["blocknum"]:
                msg = {"result":"Send block is orphan","code":2}
            else:
                msg = {"result":"Send block is from different chain","code":3}
        return msg

    def get_blocks(self, start, end):
        return self.chain[start:end+1]
