# -*- coding: utf-8 -*-
import json
import hashlib
import threading
import os
import time
from settings import *

class Blockchain:
    def __init__(self, logger, txobj, dhtobj=None):
        self.chain = []
        self.logger = logger
        self.tx = txobj
        self.dht = dhtobj
        self.headblocknum = 0
        if CHAINDUMP:
            # If chain data file exist, load data.
            if os.path.exists('.blockchain/chain.json'):
                f = open('.blockchain/chain.json', 'r')
                chain = json.load(f)
                for key in chain.keys():
                    if STORAGE == "DHT":
                        self.dht.set(key, chain[key])
                    elif STORAGE == "local":
                        self.chain.append(chain[key])
                f.close()
            else:
                # Make blockchain include genesis
                self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
                if STORAGE == "DHT":
                    self.dht.set(0, self.genesis)
                elif STORAGE == "local":
                    self.chain.append(self.genesis)
        else:
            # Make blockchain include genesis
            self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
            if STORAGE == "DHT":
                self.dht.set(0, self.genesis)
            elif STORAGE == "local":
                self.chain.append(self.genesis)

        updateheadthread = threading.Thread(target=self.update_headblocknum,)
        updateheadthread.setDaemon(True)
        updateheadthread.start()

    def update_headblocknum(self):
        while(True):
            tmp = self.headblocknum
            while(self.get_block(tmp)):
                if self.headblocknum < tmp:
                    self.headblocknum = tmp
                    self.logger.log(20,"Update head block num(%s)" % str(tmp))
                tmp = tmp + 1
            time.sleep(3)

    def generate_block(self, score):
        # Make new Block include all tx in txpool
        pool = []
        for txid in self.tx.txpool.keys():
            pool.append(self.tx.txpool[txid])
        blocknum = self.headblocknum + 1
        previous = json.dumps(self.get_block(self.headblocknum))
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
            # set block
            if STORAGE == "DHT":
                self.dht.set(block["blocknum"],block)
            elif STORAGE == "local":
                self.chain.append(block)

            self.headblocknum = block["blocknum"]
            self.logger.log(20,"Append New Block(%s) to my chain" % block["blocknum"])
            self.chain_dump()
            return True, res
        elif res["code"] == 5:
            self.headblocknum = block["blocknum"]
            return True, res
        else:
            # TODO: resolv confrict of chain -> difine consensus
            return False, res

    def rm_last_block(self):
        lastblock = self.get_block(self.headblocknum)
        for tx in lastblock["tx"]:
            self.tx.add_tx_pool(tx)

        # set block
        if STORAGE == "DHT":
            # TODO: How remove block from DHT?
            print("remove block from DHT is not implimented")
        elif STORAGE == "local":
            self.chain.pop(-1)

        self.headblocknum = self.headblocknum - 1
        self.logger.log(20,"Remove Block(%s) from my chain" % lastblock["blocknum"])

    def verify_block(self, block):
        # Verify Block
        previousblock = self.get_block(self.headblocknum)
        previous = json.dumps(previousblock)
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["blocknum"] == previousblock["blocknum"]+1:
            # new block
            if block["previous_hash"] == previoushash:
                myblock = self.get_block(block["blocknum"])
                if not myblock:
                    msg = {"result":"Checked Block has been verified","code":0}
                else:
                    # TODO don't recognize my storage block upper headblocknum
                    # TODO ここからやる！！！！
                    myblockjson = json.dumps(myblock)
                    blockjson = json.dumps(block)
                    if hashlib.sha256(myblockjson.encode('utf-8')).hexdigest() == hashlib.sha256(blockjson.encode('utf-8')).hexdigest():
                        msg = {"result":"Checked Block has been in storage","code":5}
                    else:
                        msg = {"result":"Checked Block is from different chain","code":1}
            else:
                msg = {"result":"Checked Block is from different chain","code":1}
        elif previousblock["blocknum"] < block["blocknum"]:
            # orphan block
            msg = {"result":"Checked Block is orphan","code":2}
        else:
            # old block
            jsonblock = json.dumps(block)
            myblock = json.dumps(self.get_block(block["blocknum"]))
            if hashlib.sha256(jsonblock.encode('utf-8')).hexdigest() == hashlib.sha256(myblock.encode('utf-8')).hexdigest():
                msg = {"result":"Checked Block has been in my chain","code":3}
            else:
                msg = {"result":"Checked Block is old and come from different chain","code":4}

        self.logger.log(20, msg["result"])
        return msg

    def chain_dump(self):
        if CHAINDUMP:
            chaindict = {}
            for a in range(0,self.headblocknum):
                chaindict[a] = self.get_block(a)
            savepath = '.blockchain/chain.json'
            with open(savepath, 'w') as outfile:
                json.dump(chaindict, outfile, indent=4)

    def get_chain(self, until):
        chain = []
        for a in range(0,until+1):
            chain.append(self.get_block(a))
        return chain

    def get_block(self,id):
        if STORAGE == "DHT":
            return self.get_block_from_dht(id)
        elif STORAGE == "local":
            if len(self.chain)-1 < id:
                return None
            else:
                return self.chain[id]

    def get_block_from_dht(self,id):
        block = self.dht.get(id)
        if block:
            return block
        else:
            self.logger.log(40, "Cannot get block(%s) from dht" %id)
            return None
