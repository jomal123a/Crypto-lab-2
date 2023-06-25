#!/bin/python
from transaction_utils import *
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 8081))
server.send("===cli===".encode("utf-8"))

action = input("action [t, b]: ")
if action == "t":
    tx_id = input("tx: ")
    rx_id = input("rx: ")
    amount = input("amount: ")

    tx_sk = load_key(f"client_keys/client_{tx_id}_key")

    t = Transaction(
                    tx=tx_sk.public_key(),
                    rx=load_key(f"client_keys/client_{rx_id}_key").public_key(),
                    ammount=amount,
                    t_balance=0,
                    signature=None
                )
    t.signature = t.calc_signature(tx_sk)
    t_dict = t.to_dict(to_str=True)
    print(t_dict)

    server.send(f"record {json.dumps(t_dict)}".encode('utf-8'))
    # server.send(f"record {{\"tx\": {t_dict['tx']}, \"rx\": {t_dict['rx']}, \"ammount\": {t_dict['ammount']}, \"t_balance\": 0, \"signature\": {t_dict['signature']}}}".encode('utf-8'))

elif action == "b":
    node_or = input("node or client [n, c]: ")
    key = ""
    if node_or == "n":
        pk = input("pk: ")
        tx_sk = load_key(f"keys/node_{pk}_key")
        key = serialize_rsa_public(tx_sk.public_key()).hex()
    elif node_or == "c":
        pk = input("pk: ")
        tx_sk = load_key(f"client_keys/client_{pk}_key")
        key = serialize_rsa_public(tx_sk.public_key()).hex()
    server.send(f"balance {key}".encode('utf-8'))
    balance = server.recv(2048).decode("utf8")
    print(f"balance = {balance}")