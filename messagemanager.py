# -*- coding: utf-8 -*-
import socket
import json

class MessageManager:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)
        self.peers = []

    def send(self, msgtype, msgbody, dist, res=True):
        msg = {"type": msgtype, "body":msgbody, "from":{"addr":self.addr, "port":self.port}}
        msg = json.dumps(msg)
        msg = msg.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((dist["addr"], dist["port"]))
        client.send(msg)
        if res:
            response = client.recv(4096)
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

    def recever(self):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversock.bind((self.addr, self.port))
        serversock.listen(100)

        clientsock, (client_address, client_port) = serversock.accept()
        rcvmsg = clientsock.recv(1024)
        rcvmsg = rcvmsg.decode("utf-8")

        print(rcvmsg)

        rtnmsg = rcvmsg
        clientsock.send(rtnmsg.encode("utf-8"))
