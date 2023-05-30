from json_utils import (
    init_blockchain,
    create_block,
    create_record,
    init_blockchain_from_neighbour,
    create_record_for_block,
    add_block_to_chain,
)
import threading
import time
from queue import Queue
import sys
import random
import hashlib
import json
from datetime import datetime

input_queue = Queue()
finished_pow_queue = Queue()
block_received = threading.Event()

class CommunicationThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        init_blockchain(1)
        self.block_id, self.block = create_block(0, "aaa", ["bbb", "ccc"], 2137)

    def run(self):
        while True:
            # Receive already calculated block from socket tba

            # finished_pow_queue.put(received_block)
            # Wipe out all the records from current block that are already present in a received block tba
            # block_received.set()

            # Receive a new record from socket tba
            self.block = create_record_for_block(self.block, "P.K. to najlepszy prowadzący")
            time.sleep(0.5)
            self.block = create_record_for_block(self.block, "P.K. to najgorszy prowadzący")

            # Sort by timestamp and change indices so that the oldest record is first and the newest last
            self.block['records'] = sorted(self.block['records'], key=lambda record: record['timestamp'])
            for i in range(len(self.block['records'])):
                self.block['records'][i]['index'] = i + 1

            # Send immediately to POW thread
            input_queue.put(self.block)
            break


class PowThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.block = None
        self.d = 1000

    def run(self):
        # input hold curr block for which the pow is calculated at the moment
        while True:
            # If different node calculated block then restart the calculations on a new block
            if block_received.is_set():
                self.running = False
                self.block = None
                block_received.clear()

            if not input_queue.empty():
                print('POW: fethed a new record')
                self.block = input_queue.get()
                self.running = False

            if self.running:
                # Make attempt to calculate the pow
                if self.pow_calc_attempt(self.block, self.d):
                    finished_pow_queue.put(self.block)
                    self.block = None
                    self.running = False
                    # Replace curr block pow field with calculated pow

            elif not self.running and self.block != None:
                # Check if there isnt another pow to calculate
                self.running = True

    def get_hash(self, data):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        digest = sha256_hash.digest()
        return digest

    def pow_calc_attempt(self, block, d):
        block['timestamp'] = datetime.now().timestamp()
        b = random.getrandbits(32)
        b_hex = format(b, f'08x')
        block['PoW'] = b_hex
        data = json.dumps(block).encode('utf-8')

        h_data = self.get_hash(data)
        token = self.get_hash(h_data + bytes.fromhex(b_hex))
        token_num = int.from_bytes(token, "big")

        if token_num < ((2**256) / d):
            return True

        return False


class IoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if not finished_pow_queue.empty():
                block = finished_pow_queue.get()
                print('Calculated pow for this block:')
                print(block)
                add_block_to_chain(block, 1)
                # Send calculated block to the other nodes via sockets tba


class Node:
    def __init__(self, id):
        self.id = id
        self.comm_thread = CommunicationThread()
        self.io_thread = IoThread()
        self.pow_thread = PowThread()

    def run(self):
        self.comm_thread.start()
        self.io_thread.start()
        self.pow_thread.start()

        self.comm_thread.join()
        self.io_thread.join()
        self.pow_thread.join()

def get_data_hash(block):
    json_str = json.dumps(block, sort_keys=True)
    json_bytes = json_str.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(json_bytes)
    digest = sha256_hash.digest()
    hash_integer = int.from_bytes(digest, byteorder='big')

    return hash_integer

node = Node(0)
node.run()