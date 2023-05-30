#  Crypto - lab2
Blockchain simulation

# Usage
1. Start server.py
2. For every node start an instance of app.py

Nodes accept commands from CLI:
    RECORD [data] - insert new record with content=data
    NOB - print number of confirmed blocks
    GET [n] - print n-th block
    GETALL - print whole blockchain
    GETALL [file] - print whole blockchain to file

Forks are resolved based on PoW calculation timestamp.

# Authors

Wojciech Strzelecki \
Ignacy Kowalewski \
Michał Nadolny \
Tomasz Jankowiak
