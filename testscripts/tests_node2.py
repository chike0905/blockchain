# -*- coding: utf-8 -*-
import sys
from nodemanager import *


def test_make_tx_and_send(node):
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_tx()
    node.make_tx()
    node.make_tx()

def test_make_block_and_tx(node):
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_tx()
    node.make_block(100)
    node.make_tx()
    node.make_block(100)
    node.make_tx()
    node.make_block(100)

def test_send_orphan(node):
    node.make_block(100)
    node.make_block(100)
    node.make_block(100)
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_block(100)

def test_send_orphan_and_conflicts(node):
    node.make_block(100)
    node.make_block(100)
    node.make_block(100)
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_block(100)

args = sys.argv
node = NodeManager(args[1])

test_make_block_and_tx(node)
print(node.chainmng.txmng.txpool)
