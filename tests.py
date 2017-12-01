# -*- coding: utf-8 -*-
import pytest

import json
import hashlib
from main import BlockchainService

def test_makeblock():
    bcs = BlockchainService()
    for a in range(0,5):
        bcs.make_tx()
        bcs.make_block(100)

    bcs.bc.chain[2]["previous_hash"] = hashlib.sha256("hoge".encode("utf-8")).hexdigest()

    for a in range(1,len(bcs.bc.chain)):
        previous = json.dumps(bcs.bc.chain[a-1])
        assert bcs.bc.chain[a]["previous_hash"] == hashlib.sha256(previous.encode('utf-8')).hexdigest()
