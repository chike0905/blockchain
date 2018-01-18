import hashlib

class TransactionManager:
    def __init__(self):
        self.txpool = {}

    def set(self, tx):
        txstr = json.dumps(tx)
        txhash = hashlib.sha256(lastblockstr.encode("utf-8")).hexdigest()
        self.txpool[txhash] = tx
        return txhash

    def get(self, id):
        return self.txpool[id]

    def get_all(self):
        txs = []
        for id in self.txpool.keys():
            txs.append(self.txpool[id])
        return txs

    def remove(id):
        del self.txpool[id]
        return True
