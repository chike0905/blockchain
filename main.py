# -*- coding: utf-8 -*-
import json
import sys
import hashlib
import binascii
import logging
import socket
import threading
import re

import random

# logging
logger = logging.getLogger("blcokchainlog")
logger.setLevel(10)
fh = logging.FileHandler('logger.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh.setFormatter(formatter)


genesis = {"blocknum":0,"tx":[{"id":0, "body":"hello world!"}],"previous_hash":0}
chain = [genesis]
peers = []
txpool = {}


def makeblock():
    global txpool
    pool = []
    for txid in txpool.keys():
        pool.append(txpool[txid])
    blocknum = len(chain)
    previous = json.dumps(chain[-1])
    previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
    block = {"blocknum":blocknum, "tx":pool, "previous_hash":previoushash}
    blockmsg = {"type":"block","body":block}
    txpool = {}
    print("-----------------------")
    print(json.dumps(block,indent=4,
                    ensure_ascii=False,
                    sort_keys=True))
    print("-----------------------")
    sblock = json.dumps(block)
    blockmsg = json.dumps(blockmsg)

    msg = sblock
    if len(peers) == 0:
        chain.append(block)
        logger.log(20,"Generate New Blcok(%s) (peer to send new block is not found)" % blocknum)
    else:
        for peer in peers:
            res, client = sendmsg(blockmsg, peer)
            res = json.loads(res.decode('utf-8'))
            if res["code"] == -1:
                chain.append(block)
                print(res["result"])
                logger.log(20,"Generate New Blcok(%s) (Cannot send new block to peer)" % blocknum)
            elif res["code"] == 0:
                chain.append(block)
                print(res["result"])
                logger.log(20,"Generate New Blcok(%s)" % blocknum)
            elif res["code"] == 1:
                print(res["result"])
                print("Get blocks...")
                while(True):
                    msg = str(len(chain))
                    client.send(msg.encode("utf-8"))
                    gblock = client.recv(4096)
                    if gblock == b"":
                        break
                    else:
                        gblock = json.loads(gblock.decode("utf-8"))
                        print("-----------------------")
                        print(json.dumps(gblock,indent=4,
                                                ensure_ascii=False,
                                                sort_keys=True))
                        print("-----------------------")
                        chain.append(gblock)
                        logger.log(20,"Get Blcok(%s) from peer" % gblock["blocknum"])

            elif res["code"] == 2:
                print(res["result"])
                print("Send blocks...")
                while(True):
                    peerlast = client.recv(1024)
                    peerlast = int(peerlast)
                    if peerlast == len(chain):
                        client.send(b"")
                        break
                    else:
                        sblock = json.dumps(chain[peerlast])
                        sblock = sblock.encode("utf-8")
                        client.send(sblock)
            else:
                print(res["result"])


def showchain():
    for block in chain:
        print("blcoknum: %s" % block["blocknum"])
        print("-----------------------")
        print(json.dumps(block,indent=4,
                        ensure_ascii=False,
                        sort_keys=True))
        print("-----------------------")

def sendmsg(msg, dist):
    print("Send message for "+dist)
    try:
        msg = msg.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((dist,5555))
        client.send(msg)
        response = client.recv(4096)
    except Exception as e:
        response = '{"result":"'+str(e.args)+'","code":-1}'
        response = response.encode("utf-8")
    return response, client

def rcvmsg():
    while(True):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversock.bind(("", 5555))
        serversock.listen(10)

        clientsock, (client_address, client_port) = serversock.accept()
        rcvmsg = clientsock.recv(1024)
        print('\nReceived from %s:%s' % (client_address,client_port))
        print(rcvmsg)
        rcv = json.loads(rcvmsg.decode('utf-8'))
        if rcv["type"] == "tx":
            print("recive tx")
            tx = rcv["body"]
            res = '{"result":"Tx is accepted","code":0}'
            res = res.encode('utf-8')
            clientsock.send(res)
            txpool[hashlib.sha256(tx["body"].encode('utf-8')).hexdigest()] = tx
        elif rcv["type"] == "block":
            print("recive block")
            # Block
            rcvblock = rcv["body"]
            response = checkblock(rcvblock)
            res = json.loads(response.decode("utf-8"))
            # get old block(send block)
            if res["code"] == 1:
                clientsock.send(response)
                # Get last block of peer
                while(True):
                    peerlast = clientsock.recv(1024)
                    peerlast = int(peerlast)
                    if peerlast == len(chain):
                        clientsock.send(b"")
                        break
                    else:
                        sblock = json.dumps(chain[peerlast])
                        sblock = sblock.encode("utf-8")
                        clientsock.send(sblock)
            # get orphan block(get block)
            elif res["code"] == 2:
                clientsock.send(response)
                while(True):
                    msg = str(len(chain))
                    clientsock.send(msg.encode("utf-8"))
                    gblock = clientsock.recv(4096)
                    if gblock == b"":
                        break
                    else:
                        gblock = json.loads(gblock.decode("utf-8"))
                        print("-----------------------")
                        print(json.dumps(gblock,indent=4,
                                                ensure_ascii=False,
                                                sort_keys=True))
                        print("-----------------------")
                        chain.append(gblock)
                        logger.log(20,"Get Blcok(%s) from peer" % gblock["blocknum"])
            else:
                clientsock.send(response)
                for tx in rcvblock["tx"]:
                    if tx["id"] in txpool.keys()
                        txpool.pop(tx["id"])
                chain.append(rcvblock)
            clientsock.close()

def rcvstart():
    rcvthread = threading.Thread(target=rcvmsg)
    rcvthread.setDaemon(True)
    rcvthread.start()

def checkblock(rcvblock):
    previous = json.dumps(chain[-1])
    previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
    if rcvblock["previous_hash"] == previoushash:
        print("Recive block is acceptable")
        s_msg = '{"result":"Send block is accepted","code":0}'
    else:
        print("Previous blockhash in recive block is different to my last block hash")
        if chain[-1]["blocknum"] > rcvblock["blocknum"]:
            s_msg = '{"result":"Send block is old","code":1}'
        elif chain[-1]["blocknum"] < rcvblock["blocknum"]:
            s_msg = '{"result":"Send block is orphan","code":2}'
        else:
            s_msg = '{"result":"Send block is from different chain","code":2}'
    return s_msg.encode('utf-8')

def maketx():
    # make random body
    seq='0123456789abcdefghijklmnopqrstuvwxyz'
    sr = random.SystemRandom()
    randstr = ''.join([sr.choice(seq) for i in range(50)])

    tx = {"id":hashlib.sha256(randstr.encode('utf-8')).hexdigest(),"body":randstr}
    if len(peers) == 0:
        txpool[hashlib.sha256(randstr.encode('utf-8')).hexdigest()] = tx
        logger.log(20,"Generate New TX(%s) (peer to send new tx is not found)" % tx["id"])
    else:
        for peer in peers:
            txmsg = json.dumps({"type":"tx", "body":tx})
            res, client = sendmsg(txmsg, peer)
            res = json.loads(res)
            print(res["result"])
            txpool[hashlib.sha256(randstr.encode('utf-8')).hexdigest()] = tx
            logger.log(20,"Generate New TX(%s)" % tx["id"])

def showtxpool():
    for txid in txpool.keys():
        print("-----------------------")
        print(json.dumps(txpool[txid],indent=4,
                                ensure_ascii=False,
                                sort_keys=True))
        print("-----------------------")

def addpeer():
    print("Type host address of peer")
    peer = input(">> ")
    re_addr = re.compile("((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
    if re_addr.search(peer):
        peers.append(peer)
        print("Done add peer(%s)" % peer)
    else:
        print("Input(%s) is not IPv4 address" % peer)

def rmpeer():
    counter = 0
    for peer in peers:
        print("%s:%s" %(counter,peer))
    print("Type number of peer you want remove")
    peernum = input(">> ")
    rmpeer = peers[int(peernum)]
    peers.pop(int(peernum))
    print("Done remove peer(%s)" % rmpeer)

def showpeer():
    counter = 0
    if len(peers) == 0:
        print("this node not have peer")
    else:
        for peer in peers:
            print("%s:%s" %(counter,peer))

if __name__ == "__main__":
    print("wellcome blcokchain!")
    while(True):
        command = input(">> ")
        if command == "makeblock":
            makeblock()
        elif command == "showchain":
            showchain()
        elif command == "rcv":
            rcvstart()
        elif command == "addpeer":
            addpeer()
        elif command == "rmpeer":
            rmpeer()
        elif command == "showpeer":
            showpeer()
        elif command == "maketx":
            maketx()
        elif command == "showtxpool":
            showtxpool()
        elif command == "help":
             print("makeblock - make block form tx pool")
             print("showchain - show blockchain")
             print("rcv - start reciev block")
             print("addpeer - add peer node")
             print("rmpeer - rmove peer node")
             print("showpeer - show peer node list")
             print("maketx - make TX")
             print("showtxpool - show TX pool")
             print("help - show command list")
             print("exit - exit this app")
        elif command == "exit":
            sys.exit(0)
        else:
            print("Command %s is not found" % command)
