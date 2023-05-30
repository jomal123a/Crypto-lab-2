from datetime import datetime
import random
import hashlib
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

block = Block(3)
block["index"] = 3
block["main_hash"] = "e5feba8eeda7ff1c12a3cefd4b340373e2e85e87ddd050fe40c0c1ee21a4c290"
block["extra_hashes"] = [
        "0",
        "7a2e41a4cf5dca3631c04e596aa1dcef720019c1dec5c41513ef080a6f00bc1c"
      ]

def get_hash(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    digest = sha256_hash.digest()
    return digest

def pow_calc_attempt(block, d):
    block['timestamp'] = datetime.now().timestamp()
    b = random.getrandbits(32)
    b_hex = format(b, f'08x')
    block['PoW'] = b_hex
    data = json.dumps(block).encode('utf-8')

    h_data = get_hash(data)
    token = get_hash(h_data + bytes.fromhex(b_hex))
    token_num = int.from_bytes(token, "big")
    print(token_num)

    if token_num < ((2**256) / d):
        return True

    return False

i = 0
j = 1
while not pow_calc_attempt(block, 20):
    print(f"{i}: Calculating the pow")
    i += 1

print("Pow calculated")