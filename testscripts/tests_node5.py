# -*- coding: utf-8 -*-
import sys
from nodemanager import *

args = sys.argv
node = NodeManager(args[1])

node.make_block(100)
