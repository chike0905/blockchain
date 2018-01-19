# -*- coding: utf-8 -*-
import socket
import json

class MessageManager:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.peers = []

    def send(self, msgtype, msgbody, dist, res=True):
        try:
            msg["from"] = {"addr":self.addr, "port":self.port}
            msg = json.dumps({"type": msgtype, "body":msgbody})
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
            self.logger.log(30,"Error Send message to %s:%s - %s" % (dist["addr"], dist["port"], e.args))
            response = response.encode("utf-8")
            return False, response
        return True, response

    def recever(self):
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversock.bind((self.addr, self.port))
        serversock.listen(100)

        clientsock, (client_address, client_port) = serversock.accept()
        rcvmsg = clientsock.recv(1024)
        rcvmsg = rcvmsg.encode("utf-8")

        print(rcvmsg)

        rtnmsg = rcvmsg
        clientsock.send(rtnmsg.encode("utf-8"))
