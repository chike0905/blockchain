# -*- coding: utf-8 -*-

from chainmanager import *
from messagemanager import *

class NodeManager:
    def __init__(self, addr, port=5555, inital_peer_addr=None, initial_peer_port=5555):
        self.msgmng = MessageManager(addr, port)
        self.chainmng = ChainManager(self.msgmng)

