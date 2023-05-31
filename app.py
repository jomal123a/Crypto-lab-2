#!/bin/python
from datetime import datetime
import threading
from queue import Queue
import sys
import random
import socket
import select
import io
import re
import hashlib
import json
from data import (
    Blockchain,
    Block,
    eprint
)


input_queue: Queue[Block] = Queue()
finished_pow_queue: Queue[Block] = Queue()
pow_received = threading.Event()


class CommunicationThread(threading.Thread):
    def __init__(self, ip: str = "127.0.0.1", port: int = 8081, n: int = 5):
        threading.Thread.__init__(self)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.server.connect((self.ip, self.port))
        self.sockets_list = [sys.stdin, self.server]
        self.bc = Blockchain(n)
        self.block: Block = Block(-1)

    def process_from_server(self, message: str):
        r = re.sub(r'\n', ' ', message)
        l = re.split(r'(===PoW===|===record===)', r)
        f = filter(lambda x: x != '', l)
        m = list(map(lambda x: x.strip(), f))
        for i in range(len(m)):
            command = m[i]
            if command.startswith("===record==="):
                eprint("COM: record received from node")
                i += 1
                data = m[i].strip()
                if self.block["index"] == -1:
                    self.block = self.bc.get_new_block()
                self.block.add_new_record(data)
                input_queue.put(self.block)
            elif command.startswith("===PoW==="):
                eprint("COM: PoW received from node")
                i += 1
                data = json.loads(m[i].strip())
                index = data[0]["index"]
                if self.bc.index >= index:
                    eprint("COM: FORK!!!")
                    if self.bc.chain[self.bc.index][0]["timestamp"] < data[0]["timestamp"]:
                        return
                # if self.bc.chain[index - 1][1] != data[0]["main_hash"]:
                    # eprint("COM: FORK!!!")
                pow_received.set()
                records = self.block["records"]
                self.bc.chain[index] = data
                self.bc.index = index
                diff = len(records) - len(data[0]["records"])
                if diff > 0:
                    eprint("COM: adding leftover records to new block")
                    records = records[-diff:]
                    self.block = self.bc.get_new_block()
                    for r in records:
                        self.block.add_record(r)
                    input_queue.put(self.block)
                else:
                    self.block = Block(-1)

    def process_from_stdin(self, message: str):
        if message.startswith("record "):
            eprint("COM: record received from user")
            self.server.send(message.encode('utf-8'))
            data = message[7:-1]
            if data != '':
                if self.block["index"] == -1:
                    self.block = self.bc.get_new_block()
                j = self.block.add_new_record(data)
                print(f"(block {self.bc.index + 1}, record {j})")
                input_queue.put(self.block)
        elif message.startswith("get "):
            eprint("COM: print block request")
            data = message[4:]
            try:
                i = int(data)
                print(json.dumps(self.bc.chain[i], indent=2))
            except:
                eprint("incorrect block index")
        elif message.startswith("getall "):
            eprint("COM: print all blocks to file request")
            path = message[7:-1]
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.bc.chain, indent=2))
        elif message.startswith("getall"):
            eprint("COM: print all blocks request")
            print(json.dumps(self.bc.chain, indent=2))
        elif message.startswith("size"):
            eprint("COM: print number of blocks request")
            print(self.bc.index)

    def run(self):
        while True:
            read_sockets, _, _ = select.select(self.sockets_list, [], [], 0.001)

            for socks in read_sockets:
                if socks == self.server:
                    message = socks.recv(2048).decode("utf-8")
                    self.process_from_server(message)
                else:
                    message = sys.stdin.readline()
                    if message != '\n':
                        self.process_from_stdin(message)
            sys.stdout.flush()

            if not finished_pow_queue.empty():
                while not finished_pow_queue.empty():
                    self.block = finished_pow_queue.get()
                self.block = self.bc.confirm_block(self.block)
                if self.block["index"] == -1:
                    message = "PoW " + json.dumps(self.bc.chain[self.bc.index])
                    eprint("COM: sending PoW")
                    self.server.send((message+'\n').encode('utf-8'))
                else:
                    self.block = Block(-1)
            sys.stdout.flush()


class PowThread(threading.Thread):
    def __init__(self, t: int = 10, s: int = 200000):
        threading.Thread.__init__(self)
        self.running = False
        self.block = Block(-1)
        # self.d = 2000
        self.d = t * s

    def run(self):
        # input hold curr block for which the pow is calculated at the moment
        while True:
            # If different node calculated block then restart the calculations on a new block
            if pow_received.is_set():
                eprint("POW: PoW received from node")
                self.running = False
                self.block = Block(-1)
                pow_received.clear()

            if not input_queue.empty():
                eprint('POW: fetched a new record')
                self.block = input_queue.get()
                self.running = False

            if self.running:
                # Make attempt to calculate the pow
                if self.pow_calc_attempt(self.block, self.d):
                    eprint("POW: PoW calculated")
                    finished_pow_queue.put(self.block)
                    self.block = Block(-1)
                    self.running = False
                    # Replace curr block pow field with calculated pow

            elif not self.running and self.block["index"] != -1:
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


class Node:
    def __init__(self, id):
        self.id = id
        if len(sys.argv) > 1:
            self.comm_thread = CommunicationThread(n=int(sys.argv[1]))
            self.pow_thread = PowThread(t=int(sys.argv[2]), s=int(sys.argv[3]))
        else:
            self.comm_thread = CommunicationThread()
            self.pow_thread = PowThread()

    def run(self):
        self.comm_thread.start()
        self.pow_thread.start()

        self.comm_thread.join()
        self.pow_thread.join()


node = Node(0)
node.run()
