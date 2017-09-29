# -*- coding: utf-8 -*-
import json
import sys
import hashlib
import binascii
import logging
import socket
import threading

# logging
logger = logging.getLogger("blcokchainlog")
logger.setLevel(10)
fh = logging.FileHandler('logger.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh.setFormatter(formatter)


genesis = {"blocknum":0,"tx":["hello world!"],"previous_hash":0}
chain = [genesis]


def makeblock():
    blocknum = len(chain)
    previous = json.dumps(chain[-1])
    previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
    block = {"blocknum":blocknum,"tx":[],"previous_hash":previoushash}
    print("-----------------------")
    print(json.dumps(block,indent=4,
                    ensure_ascii=False,
                    sort_keys=True))
    print("-----------------------")
    sblock = json.dumps(block)

    msg = sblock
    try:
        msg = msg.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("", 11451))
        client.send(msg)
        res = client.recv(4096)
    except ConnectionRefusedError:
        res = '{"result":"Connection refused","code":-1}'
        res = res.encode("utf-8")

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

def sendmsg(msg):
    try:
        msg = msg.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("", 11451))
        client.send(msg)
        response = client.recv(4096)
    except ConnectionRefusedError:
        response = '{"result":"Connection refused","code":-1}'
        response = response.encode("utf-8")
    return response

def rcvmsg():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind(("",11451))
    serversock.listen(10)

    NUMBER_OF_THREADS = 10
    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=worker_thread, args=(serversock, ))
        thread.daemon = True
        thread.start()

def worker_thread(serversock):
    clientsock, (client_address, client_port) = serversock.accept()
    rcvmsg = clientsock.recv(1024)
    print('\nReceived from %s:%s' % (client_address,client_port))
    print(rcvmsg)

    rcvblock = json.loads(rcvmsg.decode('utf-8'))
    response = checkblock(rcvblock)
    res = json.loads(response.decode("utf-8"))
    # get old block(send block)
    if res["code"] == 1:
        clientsock.sendall(response)
        # Get last block of peer
        while(True):
            peerlast = clientsock.recv(1024)
            peerlast = int(peerlast)
            if peerlast == len(chain):
                clientsock.sendall(b"")
                break
            else:
                sblock = json.dumps(chain[peerlast])
                sblock = sblock.encode("utf-8")
                clientsock.sendall(sblock)
    # get orphan block(get block)
    elif res["code"] == 2:
        clientsock.sendall(response)
        while(True):
            msg = str(len(chain))
            clientsock.sendall(msg.encode("utf-8"))
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
        clientsock.sendall(response)
    clientsock.close()

def checkblock(rcvblock):
    previous = json.dumps(chain[-1])
    previoushash = hashlib.sha256(previous.encode('utf-8')).hexdigest()
    if rcvblock["previous_hash"] == previoushash:
        print("Recive block is acceptable")
        chain.append(rcvblock)
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

if __name__ == "__main__":
    print("wellcome blcokchain!")
    while(True):
        command = input(">> ")
        if command == "makeblock":
            makeblock()
        elif command == "showchain":
            showchain()
        elif command == "rcvmsg":
            rcvmsg()
        elif command == "sendmsg":
            sendmsg()
        elif command == "exit":
            sys.exit(0)
        else:
            print("Command %s is not found" % command)
