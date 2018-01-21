# -*- coding: utf-8 -*-
import threading
import json

from chainmanager import *
from chainresolver import *
from messagemanager import *

class NodeManager:
    def __init__(self, addr, port=5555, inital_peer_addr=None, initial_peer_port=5555):
        self.msgmng = MessageManager(addr, port)
        self.chainmng = ChainManager()
        print("Node start at %s:%s" %(addr, str(port)))
        self.start_msg_receiver()

    def start_msg_receiver(self):
        rcvthread = threading.Thread(target=self.msg_receiver)
        #rcvthread.setDaemon(True)
        rcvthread.start()

    def msg_receiver(self):
        sock = self.msgmng.init_receiver()
        while True:
            rcvmsg, clientsock = self.msgmng.receiver(sock)
            print(rcvmsg)
            rcvmsg = json.loads(rcvmsg)
            if rcvmsg["type"] == "block":
                self.get_new_block(rcvmsg["body"], rcvmsg["from"])
            elif rcvmsg["type"] == "getblk":
                resmsg = json.dumps(self.chainmng.get_block(rcvmsg["body"]))
            elif rcvmsg["type"] == "tx":
                print("tx is not implimented")

            if rcvmsg["res"]:
                clientsock.send(resmsg.encode("utf-8"))

    def make_block(self, score):
        '''
        score: block score(int)
        '''
        newblock = self.chainmng.make_new_block(score)
        if newblock:
            self.msgmng.send_all("block", newblock)
            return True
        else:
            return False

    def get_new_block(self, block, dist):
        if self.chainmng.verify_block(block):
            self.chainmng.append_block(block)
            return True
        else:
            print("Call Chain Resolver")
            ChainResolver(self.chainmng, self.msgmng, block, dist)
            return False
