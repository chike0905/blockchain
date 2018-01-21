import json
import hashlib

class Storage:
    def __init__(self):
        self.chain = {}

    def get(self, id):
        try:
            return json.loads(self.chain[id])
        except KeyError:
            return False

    def set(self, block):
        blockstr = json.dumps(block)
        blockhash = hashlib.sha256(blockstr.encode("utf-8")).hexdigest()
        self.chain[blockhash] = blockstr
        return blockhash
