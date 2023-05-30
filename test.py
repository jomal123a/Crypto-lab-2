from datetime import datetime
from hashlib import sha256
import json


class Record(dict):
    def __init__(self, content: str):
        mapping = {
            "index": None,
            "timestamp": datetime.now().timestamp(),
            "content": content
        }
        super().__init__(mapping)


class Block(dict):
    def __init__(self, index: int):
        mapping = {
            "index": index,
            "main_hash": None,
            "extra_hashes": [],
            "PoW": None,
            "timestamp": None,
            "records": []
        }
        super().__init__(mapping)

    def add_record(self, content: str):
        self["records"].append(Record(content))
        self["records"].sort(key=lambda x: x["timestamp"])
        for i, r in enumerate(self["records"]):
            r["index"] = i


class Blockchain():
    def __init__(self, n: int, t: int):
        self.n = n
        self.t = t
        self.index = 0
        self.chain = {0: (Block(0), '0')}
        self.chain[0][0]["timestamp"] = datetime.now().timestamp()

    def to_json(self):
        return json.dumps(self.chain)
    
    def extra_hashes(self, i: int):
        if i <= self.n:
            return [self.chain[j][1] for j in range(i - 1)]
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
        return [self.chain[j][1] for j in indices]

    def get_new_block(self):
        self.index += 1
        block = Block(self.index)
        block["main_hash"] = self.chain[self.index - 1][1]
        block["extra_hashes"] = self.extra_hashes(self.index)
        self.chain[self.index] = [0,0]
        self.chain[self.index][0] = block
        self.chain[self.index][1] = sha256(json.dumps(block).encode('utf-8')).hexdigest()
        return block



bc = Blockchain(5, 10)
for i in range(20):
    bc.get_new_block()
print(bc.to_json())