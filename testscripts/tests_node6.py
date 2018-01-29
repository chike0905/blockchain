# -*- coding: utf-8 -*-
import sys
from nodemanager import *
import time
import json

def check_resolved(node):
    res, peer = node.msgmng.send("getlastblk", "", {"addr":"10.2.0.6", "port":5555})
    local = json.dumps(node.chainmng.get_block(node.chainmng.lastblock))
    print("peer:" + peer)
    print("local:" + local)
    return peer == local


# wait for node 3
time.sleep(3)

args = sys.argv
node = NodeManager(args[1])
print("==test orphan conflict Block==")
node.make_block(1000)
node.make_block(1000)
node.msgmng.add_peer({"addr":"10.2.0.6", "port":5555})
node.make_block(1000)
print(check_resolved(node))
print("==test orphan conflict Block done==")

time.sleep(3)
node.msgmng.send("shutdown", "hogehoge", {"addr":"10.2.0.6", "port":5555}, False)
node.shutdown = True
