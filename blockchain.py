# -*- coding: utf-8 -*-
import json
import hashlib
import os
from settings import *

class Blockchain:
    def __init__(self, logger, txobj, dhtobj):
        self.chain = []
        self.logger = logger
        self.tx = txobj
        self.dht = dhtobj
        if CHAINDUMP:
            # If chain data file exist, load data.
            if os.path.exists('.blockchain/chain.json'):
                f = open('.blockchain/chain.json', 'r')
                chain = json.load(f)
                for key in chain.keys():
                    self.chain.append(chain[key])
                    self.dht.set(key, chain[key])
                f.close()
            else:
                # Make blockchain include genesis
                self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
                self.chain.append(self.genesis)
        else:
            # Make blockchain include genesis
            self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
            self.chain.append(self.genesis)

    def generate_block(self, score):
        # Make new Block include all tx in txpool
        pool = []
        for txid in self.tx.txpool.keys():
            pool.append(self.tx.txpool[txid])
        blocknum = len(self.chain)
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        block = {"blocknum":blocknum, "tx":pool, "previous_hash":previoushash, "score":score}
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
            self.chain_dump()
            self.dht.set(block["blocknum"],block)
            return True, res
        else:
            # TODO: resolv confrict of chain -> difine consensus
            return False, res

    def rm_last_block(self):
        for tx in self.chain[-1]["tx"]:
            self.tx.add_tx_pool(tx)
        rmblocknum = self.chain[-1]["blocknum"]
        self.chain.pop(-1)
        self.logger.log(20,"Remove Block(%s) from my chain" % rmblocknum)

    def verify_block(self, block):
        # Verify Block
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["blocknum"] == self.chain[-1]["blocknum"]+1:
            # new block
            if block["previous_hash"] == previoushash:
                msg = {"result":"Checked Block has been verified","code":0}
            else:
                msg = {"result":"Checked Block is from different chain","code":1}
        elif self.chain[-1]["blocknum"] < block["blocknum"]:
            # orphan block
            msg = {"result":"Checked Block is orphan","code":2}
        else:
            # old block
            jsonblock = json.dumps(block)
            myblock = json.dumps(self.chain[block["blocknum"]])
            if hashlib.sha256(jsonblock.encode('utf-8')).hexdigest() == hashlib.sha256(myblock.encode('utf-8')).hexdigest():
                msg = {"result":"Checked Block has been in my chain","code":3}
            else:
                msg = {"result":"Checked Block is old and come from different chain","code":4}

        self.logger.log(20, msg["result"])
        return msg

    def chain_dump(self):
        if CHAINDUMP:
            chaindict = {}
            for a in range(0,len(self.chain)):
                chaindict[a] = self.chain[a]
            savepath = '.blockchain/chain.json'
            with open(savepath, 'w') as outfile:
                json.dump(chaindict, outfile, indent=4)

    def get_block_from_dht(self,id):
        block = self.dht.get(id)
        if block:
            return block
        else:
            self.logger.log(40, "Cannot get data from dht")
            return None
