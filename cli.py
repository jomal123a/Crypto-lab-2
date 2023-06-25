import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 8081))
server.send("===cli===".encode("utf-8"))

action = input("action [t, b]: ")
if action == "t":
    tx = input("tx: ")
    rx = input("rx: ")
    amount = input("amount: ")
    server.send(f"record {{\"tx\": {tx}, \"rx\": {rx}, \"ammount\": {amount}, \"t_balance\": 0}}".encode('utf-8'))
