# -*- coding: utf-8 -*-
import sys
from nodemanager import *

def test_send_orphan(node):
    node.make_block(100)
    node.make_block(100)
    node.make_block(100)
    node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
    node.make_block(100)

args = sys.argv
node = NodeManager(args[1])

test_send_orphan(node)
