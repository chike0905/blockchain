# -*- coding: utf-8 -*-
import json
import hashlib

import random

class Transaction:
    def __init__(self):
        self.txpool = {}

    def make_tx(self):
        # make random body
        seq='0123456789abcdefghijklmnopqrstuvwxyz'
        sr = random.SystemRandom()
        randstr = ''.join([sr.choice(seq) for i in range(50)])

        tx = {"id":hashlib.sha256(randstr.encode('utf-8')).hexdigest(),"body":randstr}
        return tx

    def show_tx_pool(self):
        for txid in self.txpool.keys():
            print("-----------------------")
            print(json.dumps(self.txpool[txid],indent=4,
                                            ensure_ascii=False,
                                            sort_keys=True))
            print("-----------------------")

    def add_tx_pool(self,tx):
        #TODO: verify TX
        self.txpool[hashlib.sha256(tx["body"].encode('utf-8')).hexdigest()] = tx
        return True
