# -*- coding: utf-8 -*-
import sys
from nodemanager import *

args = sys.argv
node = NodeManager(args[1])

print("==test make block==")

for a in range(0,3):
    node.make_block(1000)

print("==test make block done==")
