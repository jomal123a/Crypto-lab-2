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
import socket
import select
import re


input_queue = Queue()
finished_pow_queue = Queue()
block_received = threading.Event()


class CommunicationThread(threading.Thread):
    def __init__(self, ip="127.0.0.1", port=8081):
        threading.Thread.__init__(self)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.server.connect((self.ip, self.port))
        self.sockets_list = [sys.stdin, self.server]

    def process_from_server(self, message: str):
        reg = re.compile(r'\<(\d+)\> ')
        match = reg.search(message)
        sender_id = int(match.group(1))
        message = re.sub(reg, '', message)
        if message.startswith("RECORD "):
            data = message[7:]

    def run(self):
        while True:
            read_sockets, _, _ = select.select(self.sockets_list, [], [])

            for socks in read_sockets:
                if socks == self.server:
                    message = socks.recv(2048).decode("utf8")
                    print(message, end='')
                else:
                    message = sys.stdin.readline().encode("utf8")
                    if message != b'\n':
                        self.server.send(message)
            sys.stdout.flush()

            # Receive already calculated block from socket tba

            # finished_pow_queue.put(received_block)
            # Wipe out all the records from current block that are already present in a received block tba
            # block_received.set()

            # Receive a new record from socket tba
            self.block = create_record_for_block(
                self.block, "P.K. to najlepszy prowadzący")
            time.sleep(0.5)
            self.block = create_record_for_block(
                self.block, "P.K. to najgorszy prowadzący")

            # Sort by timestamp and change indices so that the oldest record is first and the newest last
            self.block['records'] = sorted(
                self.block['records'], key=lambda record: record['timestamp'])
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
                time.sleep(1)
                n = random.random()
                print('An attempt to calculate pow...')
                if n < 0.1:
                    finished_pow_queue.put(self.block)
                    self.block = None
                    self.running = False
                    # Replace curr block pow field with calculated pow

            elif not self.running and self.block != None:
                # Check if there isnt another pow to calculate
                self.running = True


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


node = Node(0)
node.run()
