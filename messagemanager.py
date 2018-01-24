# -*- coding: utf-8 -*-
import socket
import json
import re

class MessageManager:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)
        self.peers = []

    def send(self, msgtype, msgbody, dist, res=True):
        '''
        msgtype(str): block, tx, getblk, getlastblk
        msgbody(str): message body
        dist(dict): {"addr":distination address(str), "port": distination port(int)}
        '''
        msg = {"type": msgtype, "body":msgbody, "from":{"addr":self.addr, "port":self.port}, "res":res}
        msg = json.dumps(msg)
        msg = msg.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((dist["addr"], dist["port"]))
        client.send(msg)
        if res:
            response = client.recv(4096)
            response = response.decode("utf-8")
        else:
            response = None
        '''
        try:
            msg = json.dumps({"type": msgtype, "body":msgbody})
            msg["from"] = {"addr":self.addr, "port":self.port}
            msg = msg.encode('utf-8')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((dist["addr"], dist["port"]))
            client.send(msg)
            if res:
                response = client.recv(4096)
            else:
                response = None
        except Exception as e:
            response = '{"result":"'+str(e.args)+'","code":-1}'
            response = response.encode("utf-8")
            return False, response
        '''
        return True, response

    def send_all(self, msgtype, msgbody, res=False):
        '''
        msgtype(str): block,getblk
        msgbody(str): message body
        dist(dict): {"addr":distination address(str), "port": distination port(int)}
        '''
        if len(self.peers) != 0:
            for peer in self.peers:
                result, res = self.send(msgtype, msgbody, peer, res)
        else:
            result = False
        return result

    def init_receiver(self):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversock.bind((self.addr, self.port))
        serversock.listen(100)
        return serversock

    def receiver(self, serversock):
        clientsock, (client_address, client_port) = serversock.accept()
        rcvmsg = clientsock.recv(1024)
        rcvmsg = rcvmsg.decode("utf-8")
        return rcvmsg, clientsock

    def add_peer(self, peer):
        '''
        peer(dict): {"addr":peer address(str), "port": peer port(int)}
        '''
        re_addr = re.compile("((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
        if re_addr.search(peer["addr"]):
            self.peers.append(peer)
            print("Done add peer(%s:%s)" % (peer["addr"], int(peer["port"])))
            return True
        else:
            print("%s is not IPv4 address" % peer["addr"])
            return False

    def rm_peer(self, peer):
        '''
        peer(dict): {"addr":peer address(str), "port": peer port(int)}
        '''
        if peer in self.peers:
            self.peers.remove(peer)
            print("Remove peer (%s:%s)" % (peer["addr"], peer["port"]))
            return True
        else:
            print("%s:%s is not in peer" % (peer["addr"], peer["port"]))
            return False

