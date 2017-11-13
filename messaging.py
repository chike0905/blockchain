# -*- coding: utf-8 -*-
import json
import socket
import threading
import re

class Messaging:
    def __init__(self,bcobj,txobj):
        self.bc = bcobj
        self.tx = txobj
        self.peers = []

    def add_peer(self, peeraddr):
        re_addr = re.compile("((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
        if re_addr.search(peeraddr):
            self.peers.append(peeraddr)
            print("Done add peer(%s)" % peeraddr)
            return True
        else:
            print("%s is not IPv4 address" % peeraddr)
            return False

    def rm_peer(self, peernum):
        if peernum > len(self.peers)-1 or len(self.peers)-1 < 0:
            return False
        else:
            rmpeer = self.peers[peernum]
            self.peers.pop(peernum)
            print("Done remove peer(%s)" % rmpeer)
            return True

    def show_peer(self):
        counter = 0
        if len(self.peers) == 0:
            print("this node not have peer")
        else:
            for peer in self.peers:
                print("%s:%s" %(counter,peer))

    def send(self, msg, dist):
        print("Send message for "+dist)
        try:
            msg = json.dump(msg)
            msg = msg.encode('utf-8')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((dist,5555))
            client.send(msg)
            response = client.recv(4096)
        except Exception as e:
            response = '{"result":"'+str(e.args)+'","code":-1}'
            response = response.encode("utf-8")
            return response
        return True

    def start_rcv(self):
        rcvthread = threading.Thread(target=self.reciver)
        rcvthread.setDaemon(True)
        rcvthread.start()

    def reciver(self):
        while(True):
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversock.bind(("", 5555))
            serversock.listen(10)
            clientsock, (client_address, client_port) = serversock.accept()
            rcvmsg = clientsock.recv(1024)
            print('\nReceived from %s:%s' % (client_address,client_port))
            print(rcvmsg)
            rcvmsg = json.loads(rcvmsg.decode('utf-8'))
            if rcvmsg["type"] == "block":
               self.bc.add_new_block(rcvmsg["body"])
            elif rcvmsg["type"] == "tx":
               self.tx.add_tx_pool(rcvmsg["body"])
            clientsock.close()
