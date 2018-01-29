# -*- coding: utf-8 -*-
import sys
from nodemanager import *

def test_orphan(node):
    node.make_block(100)

def test_orphan_and_conflict(node):
    node.make_tx()
    node.make_block(100)

args = sys.argv
node = NodeManager(args[1])

#node.make_block(100)
#tmplast = node.chainmng.lastblock
#node.chainmng.remove_last_block()
#print(node.chainmng.get_block(tmplast))

#test_orphan(node)
test_orphan_and_conflict(node)

node.stop_msg_receiver()
