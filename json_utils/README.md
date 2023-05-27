# JSON utils module

## Author

Wojciech Strzelecki

##  Module flow

* `init_blockchain` - creates empty blockchain
* `init_blockchain_from_neighbour` - creates local copy for user based on a copy of neighbour
* `create_block` - creates block (can be empty) and returns it
* `create_record` - appends record to existing block in chain (deprecated)
* `create_record_for_block` - creates record for block given as argument
* `add_block_to_chain` - adds block to local chain and saves it to json 
