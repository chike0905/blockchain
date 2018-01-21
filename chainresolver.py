# -*- coding: utf-8 -*-
import json

class ChainResolver:
    def __init__(self, chainmng, msgmng, block, dist):
        self.chainmng = chainmng
        self.msgmng = msgmng
        self.block = block
        self.dist = dist
        print("Chain Resolver is called")
        self.resolver()

    def check_situation(self):
        lastblock = self.chainmng.get_block(self.chainmng.lastblock)
        if lastblock["blocknum"] < self.block["blocknum"]:
            return "orphan"
        elif lastblock["blocknum"] > self.block["blocknum"]:
            return "old"
        else:
            return "conflict"

    def resolv_orphan(self):
        lastblock = self.chainmng.get_block(self.chainmng.lastblock)
        target = self.block["previous_hash"]
        tmpblocks = []
        while True:
            result, res = self.msgmng.send("getblk", target, self.dist)
            res = json.loads(res)
            print(res)
            if lastblock["blocknum"] == res["blocknum"]:
                print("it is conflict!")
            else:
                if self.chainmng.verify_block(res):
                    self.chainmng.append_block(res)
                    for tmp in list(reversed(tmpblocks)):
                        if self.chainmng.verify_block(tmp):
                            self.chainmng.append_block(tmp)
                        else:
                            break
                    if self.chainmng.verify_block(self.block):
                        self.chainmng.append_block(self.block)
                    break
                else:
                    target = res["previous_hash"]
                    tmpblocks.append(res)
        return True

    def resolv_old(self):
        return True

    def resolv_conflict(self):
        return True

    def resolver(self):
        situation = self.check_situation()
        if situation == "orphan":
            self.resolv_orphan()
        elif situation == "old":
            self.resolv_old()
        elif situation == "conflict":
            self.resolv_conflict()
        return True
