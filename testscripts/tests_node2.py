# -*- coding: utf-8 -*-
import sys
from nodemanager import *

def test_make_block(node, score, times):
    for a in range(0,times):
        node.make_block(score)

def test_make_tx(node, times):
    for a in range(0,times):
        node.make_tx()

def test_make_tx_and_send(node):
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    test_make_tx(node, 3)

def test_make_block_and_tx(node, score, times):
    for a in range(0,times):
        node.make_tx()
        node.make_block(score)

def test_send_orphan(node):
    test_make_block(node, 100, 3)
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_block(100)

def test_conflict_correct(node):
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    test_make_block_and_tx(node, 1000, 1)


def test_conflict_not_correct(node):
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    test_make_block_and_tx(node, 10, 1)

def test_send_orphan_and_conflicts(node):
    test_make_block_and_tx(node, 1000, 3)
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_block(1000)

args = sys.argv
node = NodeManager(args[1])

#test_send_orphan(node)
#test_conflict_correct(node)
#test_conflict_not_correct(node)
test_send_orphan_and_conflicts(node)
