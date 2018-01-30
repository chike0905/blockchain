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
            self.resolv_old(self.block)
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

    def resolv_old(self, block):
        print("it is old")
        target = self.chainmng.get_block_id(block)
        localblock = self.chainmng.get_block(target)
        if not localblock:
            print("it is old and conflict!")
            self.resolv_conflict(block)
        return True

    def resolv_conflict(self, block):
        print("it is conflict")
        forkpoint, peerblock = self.search_fork_point(block)
        localblock = self.get_local_conflict_block(forkpoint)
        print("Conflict start from %s" %localblock["blocknum"])
        if localblock["score"] >= peerblock["score"]:
            print("local is corect")
            return False
        else:
            print("peer is corect")
            while not self.chainmng.verify_block(peerblock):
                self.chainmng.remove_last_block()
            self.chainmng.append_block(peerblock)
            return True

    def search_fork_point(self, block):
        tmp = block
        while not self.chainmng.get_block(tmp["previous_hash"]):
            result, res = self.msgmng.send("getblk", tmp["previous_hash"], self.dist)
            tmp = json.loads(res)
        return tmp["previous_hash"], tmp

    def get_local_conflict_block(self, forkpoint):
        tmp = self.chainmng.get_block(self.chainmng.lastblock)
        while forkpoint != tmp["previous_hash"]:
            tmp = self.chainmng.get_block(tmp["previous_hash"])
        return tmp

    def resolv_orphan(self, block):
        lastblock = self.chainmng.get_block(self.chainmng.lastblock)
        target = block["previous_hash"]
        tmpblocks = []
        while True:
            result, res = self.msgmng.send("getblk", target, self.dist)
            res = json.loads(res)
            if lastblock["blocknum"] == res["blocknum"]:
                print("it is orphan and conflict!")
                if self.resolv_conflict(res):
                    self.resolv_orphan(block)
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
