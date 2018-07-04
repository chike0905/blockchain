import hashlib
import json

# tmp
import random

class Transaction:
    def __init__(self, jsontx=None):
        self.id = None
        if not jsontx:
            # TMP:make random body
            seq='0123456789abcdefghijklmnopqrstuvwxyz'
            sr = random.SystemRandom()
            self.body = ''.join([sr.choice(seq) for i in range(50)])
        else:
            self.loadjson(jsontx)
        self.setid()
    '''
    set id
    '''
    def setid(self):
        self.id = hashlib.sha256(self.body.encode('utf-8')).hexdigest()

    '''
    dump to json
    '''
    def dumpjson(self):
        jsontx = json.dumps({"id": self.id, "body": self.body})
        return jsontx

    '''
    load from json
    '''
    def loadjson(self, jsontx):
        tx = json.loads(jsontx)
        self.body = tx["body"]
