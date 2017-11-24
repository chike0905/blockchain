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
            return True, res
        else:
            # TODO: resolv confrict of chain -> difine consensus
            return False, res

    def rm_last_block(self):
        for tx in self.chain[-1]["tx"]:
            self.tx.add_tx_pool(tx)
        self.chain.pop(-1)

    def verify_block(self, block):
        # Verify Block
        previous = json.dumps(self.chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["blocknum"] == self.chain[-1]["blocknum"]+1:
            if block["previous_hash"] == previoushash:
                msg = {"result":"Checked Block has been verified","code":0}
            else:
                msg = {"result":"Checked Block is from different chain","code":1}
        elif self.chain[-1]["blocknum"] < block["blocknum"]:
            msg = {"result":"Checked Block is orphan","code":2}
        else:
            # TODO:this check is false. check that checked block["previous_hash"] and hash(self.bc.chain[block["blocknum"]-1])
            if block["previous_hash"] == self.chain[block["blocknum"]]["previous_hash"]:
                msg = {"result":"Checked Block has been in my chain","code":3}
            else:
                msg = {"result":"Checked Block is from different chain","code":4}

        self.logger.log(20, msg["result"])
        return msg
