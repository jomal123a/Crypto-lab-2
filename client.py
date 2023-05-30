import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "127.0.0.1"
port = 8081

server.connect((ip, port))

sockets_list = [sys.stdin, server]
while True:

  read_sockets, _, _ = select.select(sockets_list, [], [])

  for socks in read_sockets:
    if socks == server:
      message = socks.recv(2048).decode("utf8")
      print(message, end='')
    else:
      message = sys.stdin.readline()
      if message != '\n':
        server.send(message.encode("utf8"))
  sys.stdout.flush()
