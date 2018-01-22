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

    def resolver(self):
        situation = self.check_situation()
        if situation == "orphan":
            self.resolv_orphan(self.block)
        elif situation == "old":
            self.resolv_old()
        elif situation == "conflict":
            self.resolv_conflict(self.block)
        return True

    def check_situation(self):
        lastblock = self.chainmng.get_block(self.chainmng.lastblock)
        if lastblock["blocknum"] < self.block["blocknum"]:
            return "orphan"
        elif lastblock["blocknum"] > self.block["blocknum"]:
            return "old"
        else:
            return "conflict"

    def resolv_old(self):
        print("it is old")
        return True

    def resolv_conflict(self, block):
        print("it is conflict")
        target = block["previous_hash"]
        localblock = self.chainmng.get_block(self.chainmng.lastblock)
        localtarget = localblock["previous_hash"]
        conflict = {"local": localblock, "peer":block}
        while True:
            result, res = self.msgmng.send("getblk", target, self.dist)
            peerblock = json.loads(res)
            localblock = self.chainmng.get_block(localtarget)
            if peerblock["previous_hash"] == localblock["previous_hash"]:
                print("Conflict start from %s" %localblock["blocknum"])
                if conflict["local"]["score"] >= conflict["peer"]["score"]:
                    print("local is corect")
                    return False
                else:
                    print("peer is corect")
                    while not self.chainmng.verify_block(conflict["peer"]):
                        self.chainmng.remove_last_block()
                    self.chainmng.append_block(conflict["peer"])
                    return True
            else:
                conflict = {"local": localblock, "peer":peerblock}
                target = peerblock["previous_hash"]
                localtarget = localblock["previous_hash"]

    def resolv_orphan(self, block):
        lastblock = self.chainmng.get_block(self.chainmng.lastblock)
        target = block["previous_hash"]
        tmpblocks = []
        while True:
            result, res = self.msgmng.send("getblk", target, self.dist)
            res = json.loads(res)
            if lastblock["blocknum"] == res["blocknum"]:
                print("it is orphan and conflict!")
                self.resolv_conflict(res)
                break
            else:
                if self.chainmng.verify_block(res):
                    self.chainmng.append_block(res)
                    for tmp in list(reversed(tmpblocks)):
                        if self.chainmng.verify_block(tmp):
                            self.chainmng.append_block(tmp)
                        else:
                            break
                    if self.chainmng.verify_block(block):
                        self.chainmng.append_block(block)
                    break
                else:
                    target = res["previous_hash"]
                    tmpblocks.append(res)
        return True
