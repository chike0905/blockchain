# -*- coding: utf-8 -*-
#import pytest
import sys

import json
import hashlib
from main import BlockchainService
from time import sleep

def test_make_block_include_tx(addr):
    bcs = BlockchainService(myaddr=addr, myport="5555")
    sleep(10)
    for a in range(0,5):
        bcs.make_tx()
        bcs.make_block(100)
    sleep(10)
    for a in range(1,len(bcs.bc.chain)):
        previous = json.dumps(bcs.bc.chain[a-1])
        assert bcs.bc.chain[a]["previous_hash"] == hashlib.sha256(previous.encode('utf-8')).hexdigest()
    bcs.shutdown()

args = sys.argv
test_make_block_include_tx(args[1])
