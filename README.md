#  Crypto - lab2
Blockchain simulation

# Usage
1. Start server.py
2. For every node start an instance of app.py

Nodes accept commands from CLI:
- record data - insert new record with content=data
- size - print number of confirmed blocks
- get n - print n-th block
- getall - print whole blockchain
- getall file - print whole blockchain to file

Forks are resolved based on PoW calculation timestamp.

3. Run a single app.py with arguments: "n test k" to quickly generate a blockchain with k blocks and n sidelinks

# Authors

Wojciech Strzelecki \
Ignacy Kowalewski \
Michał Nadolny \
Tomasz Jankowiak
