# -*- coding: utf-8 -*-
import pytest

import json
import hashlib
from main import BlockchainService

def test_make_block_include_tx():
    bcs = BlockchainService("192.168.56.1")
    for a in range(0,5):
        bcs.make_tx()
        bcs.make_block(100)

    for a in range(1,len(bcs.bc.chain)):
        previous = json.dumps(bcs.bc.chain[a-1])
        assert bcs.bc.chain[a]["previous_hash"] == hashlib.sha256(previous.encode('utf-8')).hexdigest()

    for a in range(0,len(bcs.bc.chain)):
        res, resmsg = bcs.msg.send({"type":"getblk", "body":{"blocknum":a}}, {"addr":"192.168.56.1", "port":"5555"})
        print(resmsg)
    bcs.shutdown()
