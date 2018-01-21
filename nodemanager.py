# -*- coding: utf-8 -*-

from chainmanager import *
from messagemanager import *

class NodeManager:
    def __init__(self, addr, port=5555, inital_peer_addr=None, initial_peer_port=5555):
        self.msgmng = MessageManager(addr, port)
        self.chainmng = ChainManager()
        print("Node start at %s:%s" %(addr, str(port)))
        self.msg_reciver()

    def msg_reciver(self):
        sock = self.msgmng.init_reciever()
        while True:
            rcvmsg, clientsock = self.msgmng.reciever(sock)
            print(recvmsg)
            clientsock.send(rtnmsg.encode("utf-8"))
