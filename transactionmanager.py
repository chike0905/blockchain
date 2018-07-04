import hashlib
import random
import json
import primitivs.transaction as TX

class TransactionManager:
    def __init__(self):
        self.txpool = {}

    def set(self, tx):
        self.txpool[tx.id] = tx.dumpjson()
        return tx.id

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
        tx = TX.Transaction()
        self.set(tx)
        return tx
