# -*- coding: utf-8 -*-
import json
import hashlib

from transactionmanager import *
from storage import *

class ChainManager:
    def __init__(self):
        self.storage = Storage()
        self.txmng = TransactionManager()
        self.genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
        self.lastblock = self.storage.set(self.genesis)

    def make_new_block(self, score):
        lastblock = self.storage.get(self.lastblock)
        lastblockstr = json.dumps(lastblock)
        txs = self.txmng.get_all()
        previoushash = hashlib.sha256(lastblockstr.encode("utf-8")).hexdigest()
        newblock = {
                "blocknum":int(lastblock["blocknum"]) + 1,
                "tx":txs,
                "previous_hash":previoushash,
                "score":score
                }
        if self.verify_block(newblock):
            self.append_block(newblock)
            return newblock
        else:
            return False

    def verify_block(self, block):
        lastblock = self.storage.get(self.lastblock)
        lastblockstr = json.dumps(lastblock)
        previoushash = hashlib.sha256(lastblockstr.encode("utf-8")).hexdigest()
        if previoushash == block["previous_hash"]:
            return True
        else:
            return False

    def append_block(self, block):
        self.lastblock = self.storage.set(block)
        print("New Block(blocknum:%s id:%s) is appended to my chain" %(block["blocknum"], self.lastblock))

    def get_block(self, id):
        return self.storage.get(id)
