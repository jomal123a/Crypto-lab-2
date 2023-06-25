#!/bin/python
import socket
from _thread import start_new_thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "127.0.0.1"
port = 8081

server.bind((ip, port))
server.listen()

clients = {}
nodes = []


def clientthread(conn, my_id):
    message = conn.recv(2048).decode("utf8")
    if message == "===node===":
        nodes.append(my_id)
        my_idd = "node " + str(my_id)
        print("<" + my_idd + "> connected")
        while True:
            try:
                message = conn.recv(2048).decode("utf8")
                if message and message != '\n':
                    print("<" + my_idd + "> " + message, end='')
                    if message.startswith("record "):
                        message = "===record=== " + message[7:]
                        broadcast(message.encode("utf8"), conn)
                    elif message.startswith("PoW "):
                        message = "===PoW=== " + message[4:]
                        broadcast(message.encode("utf8"), conn)
                    elif message.startswith("===balance=== "):
                        print()
                        l = message.split()
                        idd_ = l[1]
                        balance = l[2]
                        message = f"{balance}"
                        for client, idd in clients.items():
                            if idd == int(idd_):
                                try:
                                    client.send(message.encode('utf-8'))
                                    break
                                except:
                                    remove(client, clients[client])
                else:
                    remove(conn, my_idd)
                    return
            except:
                continue
    elif message == "===cli===":
        my_idd = "cli " + str(my_id)
        print("<" + my_idd + "> connected")
        while True:
            try:
                message = conn.recv(2048).decode("utf8")
                if message and message != '\n':
                    print("<" + my_idd + "> " + message)
                    if message.startswith("record "):
                        message = "===record=== " + message[7:]
                        broadcast(message.encode("utf8"), conn)
                    elif message.startswith("balance "):
                        message = "===balance===###" + str(my_id) + "###" + message[8:]
                        for client, idd in clients.items():
                            if idd in nodes:
                                try:
                                    client.send(message.encode('utf-8'))
                                    break
                                except:
                                    remove(client, clients[client])
                else:
                    remove(conn, my_idd)
                    return
            except:
                continue


def broadcast(message, connection):
    for client, idd in clients.items():
        if client != connection and idd in nodes:
            try:
                client.send(message)
            except:
                remove(client, clients[client])


def remove(client, my_id):
    print("<" + str(my_id) + "> disconnected")
    if client in clients:
        clients.pop(client)
    client.close()
    del client


next_id = 0

while True:
    conn, addr = server.accept()
    clients[conn] = next_id
    start_new_thread(clientthread, (conn, next_id))
    next_id += 1
