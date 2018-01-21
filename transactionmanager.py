import hashlib
import random
import json

class TransactionManager:
    def __init__(self):
        self.txpool = {}

    def set(self, tx):
        txstr = json.dumps(tx)
        txhash = hashlib.sha256(tx["body"].encode("utf-8")).hexdigest()
        self.txpool[txhash] = tx
        return txhash

    def get(self, id):
        return self.txpool[id]

    def get_all(self):
        txs = []
        for id in self.txpool.keys():
            txs.append(self.txpool[id])
        return txs

    def remove(self, id):
        del self.txpool[id]
        return True

    def make_new_tx(self):
        # make random body
        seq='0123456789abcdefghijklmnopqrstuvwxyz'
        sr = random.SystemRandom()
        randstr = ''.join([sr.choice(seq) for i in range(50)])

        tx = {"id":hashlib.sha256(randstr.encode('utf-8')).hexdigest(),"body":randstr}
        self.set(tx)
        return tx
