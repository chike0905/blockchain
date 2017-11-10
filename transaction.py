# -*- coding: utf-8 -*-
import json
import hashlib
import logging
import re

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
        self.txpool[hashlib.sha256(randstr.encode('utf-8')).hexdigest()] = tx
        logger.log(20,"Generate New TX(%s)" % tx["id"])

    def show_tx_pool(self):
        for txid in self.txpool.keys():
            print("-----------------------")
            print(json.dumps(self.txpool[txid],indent=4,
                                            ensure_ascii=False,
                                            sort_keys=True))
            print("-----------------------")
