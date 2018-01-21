# -*- coding: utf-8 -*-
import sys
from nodemanager import *

args = sys.argv
node = NodeManager(args[1])
node.msgmng.add_peer({"addr":"10.2.0.2", "port":5555})
node.make_block(100)
