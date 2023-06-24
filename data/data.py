from datetime import datetime
from hashlib import sha256
import json
import sys
from math import sqrt, ceil
import numpy.random as rand

def eprint(v: bool = True, *args, **kwargs):
    if v:
        print('\033[93m', file=sys.stderr, end='')
        print(*args, file=sys.stderr, **kwargs, end='')
        print('\033[0m', file=sys.stderr)


class Record(dict):
    def __init__(self, content):
        mapping = {
            "index": None,
            "timestamp": datetime.now().timestamp(),
            "content": content
        }
        super().__init__(mapping)

    def __eq__(self, other):
        return self["timestamp"] == other["timestamp"] and self["content"] == other["content"]


class Block(dict):
    def __init__(self, index: int = 0, mapp: dict = {}):
        if not mapp:
            mapping = {
                "index": index,
                "main_hash": None,
                "extra_hashes": [],
                "PoW": None,
                "timestamp": None,
                "records": []
            }
            super().__init__(mapping)
        else:
            super().__init__(mapp)
        

    def add_new_record(self, content):
        r = Record(content)
        self["records"].append(r)
        self["records"].sort(key=lambda x: x["timestamp"])
        j = 0
        for i, r_ in enumerate(self["records"]):
            r_["index"] = i
            if r == r_:
                j = i
        return j 
    
    def add_new_prize_record(self, content):        
        for i, r_ in enumerate(self["records"]):
            if r_['content']['tx'] == "SERVER":
                del self["records"][i]

        r = Record(content)
        self["records"].append(r)
        self["records"].sort(key=lambda x: x["timestamp"])
        j = 0
        for i, r_ in enumerate(self["records"]):
            r_["index"] = i
            if r == r_:
                j = i
        return j 

    def add_record(self, r: Record):
        self["records"].append(r)
        self["records"].sort(key=lambda x: x["timestamp"])
        j = 0
        for i, r_ in enumerate(self["records"]):
            r_["index"] = i
            if r == r_:
                j = i
        return j 

    def equals(self, r: Record):
        return self["timestamp"] == r["timestamp"] and self["content"] == r["content"]

def harm(n, k):
    if n == 0:
        return 0.0
    h = 1.0
    for i in range(2, n + 1):
        h += 1 / pow(i, k)
    return h

class Blockchain():
    def __init__(self, n: int):
        self.n = n
        self.index = 0
        self.chain = {0: [Block(0), '0']}
        self.chain[0][0]["timestamp"] = datetime.now().timestamp()

    def to_json(self):
        return json.dumps(self.chain)

    def extra_hashes(self, i: int):
        if i <= self.n + 1:
            return [(j, self.chain[j][1]) for j in range(i - 1)]
        
        xs = [self.chain[i - 1][1]]

        for j in range(1, self.n):
            xs.append(sha256((xs[j - 1] + str(j)).encode('utf-8')).hexdigest())
        
        rand.seed(sum(map(lambda x: int(x, 16), xs)) % 2 ** 32)
        dist = [1/(pow(i - j - 1, self.n) * harm(i, self.n)) for j in range(0, i - 1)]
        indices = rand.choice(range(i - 1), size=self.n, replace=False, p=dist)

        return [(int(j), self.chain[j][1]) for j in indices]
    
    def extra_hashes_old(self, i: int):
        if i <= self.n + 1:
            return [(j, self.chain[j][1]) for j in range(i - 1)]
        xs = [self.chain[i - 1][1]]
        for j in range(1, self.n):
            xs.append(sha256((xs[j - 1] + str(j)).encode('utf-8')).hexdigest())
        indices = [int(xs[0], 16) % (i - self.n)]
        module = i - self.n + 1
        for j in range(1, self.n):
            n_ = int(xs[j], 16) % module
            try:
                k = indices.index(n_)
                indices.append(module - 1)
            except:
                indices.append(n_)
            module += 1
        return [(j, self.chain[j][1]) for j in indices]

    def get_new_block(self, v: bool = True):
        eprint(v, f"creating new block {self.index + 1}")
        block = Block(self.index + 1)
        block["main_hash"] = self.chain[self.index][1]
        block["extra_hashes"] = self.extra_hashes(self.index + 1)
        return block

    def confirm_block(self, block: Block, v: bool = True):
        if self.index + 1 != block["index"]:
            return Block(-2)
        self.index += 1
        eprint(v, f"confirming block {self.index}")
        self.chain[self.index] = [block, sha256(
            json.dumps(block).encode('utf-8')).hexdigest()]
        return Block(-1)
