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
        self.key = "hogehoge"
        self.shutdown = False
        self.rcvthread = self.start_msg_receiver()
        self.server = self.start_server()

    def start_server(self):
        thread = threading.Thread(target=self.shutdown_checker)
        #thread.setDaemon(True)
        thread.stop_event = threading.Event()
        thread.start()
        return thread

    def shutdown_checker(self):
        while True:
            if self.shutdown:
                print("Shutdown node")
                self.server.stop_event.set()
                self.stop_msg_receiver()
                break

    def start_msg_receiver(self):
        rcvthread = threading.Thread(target=self.msg_receiver)
        rcvthread.setDaemon(True)
        rcvthread.stop_event = threading.Event()
        rcvthread.start()
        return rcvthread

    def stop_msg_receiver(self):
        self.rcvthread.stop_event.set()
        return True

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
            elif rcvmsg["type"] == "getlastblk":
                resmsg = json.dumps(self.chainmng.get_block(self.chainmng.lastblock))
            elif rcvmsg["type"] == "tx":
                self.get_new_tx(rcvmsg["body"], rcvmsg["from"])
            elif rcvmsg["type"] == "shutdown":
                if rcvmsg["body"] == self.key:
                    self.shutdown = True
                else:
                    print("shutdown request key is different")

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

    def get_new_tx(self, tx, dist):
        if tx["id"] in self.chainmng.txmng.txpool.keys():
            return False
        else:
            self.chainmng.txmng.set(tx)
            return True

    def make_tx(self):
        tx = self.chainmng.txmng.make_new_tx()
        self.chainmng.txmng.set(tx)
        self.msgmng.send_all("tx", tx)
        return True
