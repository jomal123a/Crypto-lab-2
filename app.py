from json_utils import (
    init_blockchain,
    create_block,
    create_record,
    init_blockchain_from_neighbour,
    create_record_for_block,
    add_block_to_chain,
)


init_blockchain(1)
block_id, block = create_block(0, "aaa", ["bbb", "ccc"], 2137)
block = create_record_for_block(block, "P.K. to najlepszy prowadzący")
block = create_record_for_block(block, "P.K. to najlepszy prowadzący")
block = create_record_for_block(block, "P.K. to najlepszy prowadzący")
add_block_to_chain(block, 1)

init_blockchain_from_neighbour(2, 1)
block_id, block = create_block(block_id, "aaa", ["bbb", "ccc"], 2137)
block = create_record_for_block(block, "M.S. to najlepszy prowadzący")
block = create_record_for_block(block, "M.S. to najlepszy prowadzący")
block = create_record_for_block(block, "M.S. to najlepszy prowadzący")
add_block_to_chain(block, 2)
