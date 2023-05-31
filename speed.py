from data import (
    Blockchain,
    Block,
    eprint
)
import hashlib
from datetime import datetime
import json
import random
import time

block = Block(0)
block.add_new_record("123")
block.add_new_record("123")
block.add_new_record("123")
block.add_new_record("123")
block.add_new_record("123")
block.add_new_record("123")
block.add_new_record("123")


def get_hash(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    digest = sha256_hash.digest()
    return digest


def pow_calc_attempt(block):
    block['timestamp'] = datetime.now().timestamp()
    b = random.getrandbits(32)
    b_hex = format(b, f'08x')
    block['PoW'] = b_hex
    data = json.dumps(block).encode('utf-8')

    h_data = get_hash(data)
    token = get_hash(h_data + bytes.fromhex(b_hex))
    token_num = int.from_bytes(token, "big")


n = 10 ** 6
start = time.process_time_ns()
for i in range(n):
    pow_calc_attempt(block)
one = (time.process_time_ns() - start) / n
print(10**9 / one)
