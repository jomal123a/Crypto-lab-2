#!/bin/python
import socket
from _thread import start_new_thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "127.0.0.1"
port = 8081

server.bind((ip, port))
server.listen()

clients = {}


def clientthread(conn, my_id):
  conn.send('Welcome to blockchain\n'.encode("utf8"))
  while True:
    try:
      message = conn.recv(2048).decode("utf8")
      if message and message != '\n':
        print("<" + str(my_id) + "> " + message, end='')
        broadcast(message.encode("utf8"), conn)
      else:
        remove(conn, my_id)
        return
    except:
      continue


def broadcast(message, connection):
  for client in clients:
    if client != connection:
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
  print("<" + str(next_id) + "> connected")
  start_new_thread(clientthread, (conn, next_id))
  next_id += 1
