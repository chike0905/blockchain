# -*- coding: utf-8 -*-
import sys
from nodemanager import *

def test_orphan_and_conflict(node):
    node.make_tx()
    node.make_block(100)

args = sys.argv
node = NodeManager(args[1])

