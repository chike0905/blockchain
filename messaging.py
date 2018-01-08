# -*- coding: utf-8 -*-
import json
import socket
import threading
import re
import hashlib


class Messaging:
    def __init__(self, logger, bcobj, txobj, dhtobj=None):
        self.bc = bcobj
        self.tx = txobj
        self.peers = []
        self.logger = logger
        self.dht = dhtobj

    def add_peer(self, peeraddr, peerport):
        re_addr = re.compile("((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
        if re_addr.search(peeraddr):
            self.peers.append({"addr":peeraddr, "port":int(peerport)})
            print("Done add peer(%s:%s)" % (peeraddr, peerport))
            self.logger.log(20,"Add peer(%s:%s)" % (peeraddr, peerport))
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
            self.logger.log(20,"remove peer(%s)" % rmpeer)
            return True

    def show_peer(self):
        counter = 0
        if len(self.peers) == 0:
            print("this node not have peer")
        else:
            for peer in self.peers:
                print("%s - %s:%s" %(counter, peer["addr"], peer["port"]))

    def send(self, msg, dist):
        self.logger.log(20,"Send %s message to %s:%s" % (msg["type"], dist["addr"], dist["port"]))
        try:
            msg = json.dumps(msg)
            msg = msg.encode('utf-8')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((dist["addr"], dist["port"]))
            client.send(msg)
            response = client.recv(4096)
        except Exception as e:
            response = '{"result":"'+str(e.args)+'","code":-1}'
            self.logger.log(30,"Error Send message to %s:%s - %s" % (dist["addr"], dist["port"], e.args))
            response = response.encode("utf-8")
            return False, response
        return True, response

    def start_rcv(self, addr, port):
        rcvthread = threading.Thread(target=self.receiver, args=([addr,int(port)],))
        rcvthread.setDaemon(True)
        rcvthread.start()
        self.logger.log(20,"Start recieving message")

    def receiver(self, host):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversock.bind((host[0], host[1]))
        serversock.listen(100)
        while(True):
            clientsock, (client_address, client_port) = serversock.accept()
            rcvmsg = clientsock.recv(1024)
            #print("rcvmsg:%s" %rcvmsg)
            try:
                rcvmsg = json.loads(rcvmsg.decode('utf-8'))
                if rcvmsg["type"] == "block":
                    self.logger.log(20,"Receive Block from %s:%s" % (client_address,client_port))
                    res, resadd = self.bc.add_new_block(rcvmsg["body"])
                    if not res:
                        if resadd["code"] == 1:
                            self.logger.log(20,"Receive Block from %s:%s comes from different chain" % (client_address, client_port))
                            self.resolv_different_chain(rcvmsg["body"], client_address, client_port)
                            self.resolv_orphan_block(rcvmsg["body"], client_address)
                        elif resadd["code"] == 2:
                            self.logger.log(20,"Receive Block from %s:%s is orphan" % (client_address, client_port))
                            self.resolv_orphan_block(rcvmsg["body"], client_address, client_port)
                        elif resadd["code"] == 3:
                            self.logger.log(20,"Receive Block from %s:%s has been in my chain" % (client_address, client_port))
                        elif resadd["code"] == 5:
                            self.logger.log(20,"Receive Block from %s:%s has been in my storage" % (client_address, client_port))


                elif rcvmsg["type"] == "tx":
                   self.logger.log(20,"Receive Transaction from %s:%s" % (client_address, client_port))
                   self.tx.add_tx_pool(rcvmsg["body"])

                elif rcvmsg["type"] == "getblk":
                    self.logger.log(20,"Receive Get Block(%s) Request from %s:%s" % (str(rcvmsg["body"]["blocknum"]), client_address, client_port))
                    if self.bc.headblocknum >= rcvmsg["body"]["blocknum"]:
                        block = self.bc.get_block(rcvmsg["body"]["blocknum"])
                        rtnmsg = {"code":0,"body":block}
                    else:
                        rtnmsg = {"code":-1,"body":"index out of range"}
                    rtnmsg = json.dumps(rtnmsg)
                    rtnmsg = rtnmsg.encode("utf-8")
                    clientsock.send(rtnmsg)
                elif rcvmsg["type"] == "DHT":
                    #print("dhtmsg:%s"%rcvmsg["body"])
                    rtnmsg = self.dht.local_.run(rcvmsg["body"])
                    #print("dhtrtnmsg:%s"%rtnmsg)

                    clientsock.send(rtnmsg.encode("utf-8"))
            except json.decoder.JSONDecodeError:
                rtnmsg = ""
                self.logger.log(20,"Receive message decode error from %s:%s" % (client_address,client_port))
                clientsock.send(rtnmsg.encode("utf-8"))
            clientsock.close()

    def check_new_block_for_chain(self,chain,block):
        previous = json.dumps(chain[-1])
        previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
        if block["previous_hash"] == previoushash:
            return True
        else:
            return False

    def resolv_different_chain(self, rcvblock, client_address, client_port):
        for blocknum in reversed(range(1,rcvblock["blocknum"])):
            res, resmsg = self.send({"type":"getblk", "body":{"blocknum":blocknum}}, {"addr":client_address, "port":client_port})
            resmsg = json.loads(resmsg.decode('utf-8'))
            block = resmsg["body"]
            if self.check_new_block_for_chain(self.bc.chain[0:block["blocknum"]], block):
                if block["score"] > self.bc.chain[block["blocknum"]]["score"]:
                    for rmblocknum in range(blocknum,len(self.bc.chain)):
                        self.bc.rm_last_block()
                    self.bc.add_new_block(block)
                break

    def resolv_orphan_block(self, block, client_address, client_port):
        for blocknum in range(len(self.bc.chain), block["blocknum"]+1):
            res, resmsg = self.send({"type":"getblk", "body":{"blocknum":blocknum}}, {"addr":client_address, "port":client_port})
            resmsg = json.loads(resmsg.decode('utf-8'))
            self.logger.log(20,"Get Block(%s) from %s" %(str(blocknum), client_address))
            res, rescode = self.bc.add_new_block(resmsg["body"])
            if not res:
                break;
