import json
from datetime import datetime

BLOCK_FIELDS = (
    "index",
    "main_hash",
    "extra_hashes",
    "pow",
    "timestamp",
    "records",
)

RECORD_FIELDS = (
    "index",
    "timestamp",
    "content",
)

FILE_NAME = "blockchain.json"


class ValidationError(Exception):
    pass

class Block(dict):
    def __init__(self, index: int):
        self.id = index
        mapping = {
            "index": index,
            "main_hash": None,
            "extra_hashes": [],
            "b": None,
            "timestamp": None,
            "records": []
        }
        super.__init__(mapping)

    def get_index(self):
        return self["index"]
    
    def set_index(self, index: int):
        self["index"] = index
    

def _validate_block(block: dict) -> bool:
    return all([key in block for key in BLOCK_FIELDS])


def _validate_record(record: dict) -> bool:
    return all([key in record for key in RECORD_FIELDS])


def _validate(data: dict) -> bool:
    for block in data["blocks"]:
        if not _validate_block(block):
            return False

        for record in block["records"]:
            if not _validate_record(record):
                return False

    return True


def init_blockchain(id_: int) -> None:
    _initializer = {
        "blocks": [
            {
                "index": 0,
                "main_hash": "x",
                "extra_hashes": [],
                "pow": 0,
                "timestamp": datetime.now().timestamp(),
                "records": [],
            }
        ]
    }  # add block 0
    with open(f"{id_}_{FILE_NAME}", "w") as f:
        f.write(json.dumps(_initializer))


def init_blockchain_from_neighbour(id_: int, neighbour_id: int):
    _initializer = load_blockchain(neighbour_id)
    with open(f"{id_}_{FILE_NAME}", "w") as f:
        f.write(json.dumps(_initializer))


def load_blockchain(id_: int) -> dict:
    with open(f"{id_}_{FILE_NAME}", "r") as f:
        json_ = json.loads(f.read())

    if not _validate(json_):
        raise ValidationError("Blockchain has incorrect structure")

    return json_


def save_blockchain(id_: int, chain: dict) -> None:
    with open(f"{id_}_{FILE_NAME}", "w") as f:
        f.write(json.dumps(chain))


def create_block(
    id_: int,
    main_hash: str,
    extra_hashes: list[str],
    b: str | int,
    records: list | None = None,
) -> tuple[int, dict]:
    # chain = load_blockchain(user_id)
    id_ += 1
    block = {}

    block["index"] = id_
    block["main_hash"] = main_hash
    block["extra_hashes"] = extra_hashes
    block["pow"] = b  # nonce
    block["timestamp"] = datetime.now().timestamp()
    block["records"] = records if records else []
    # chain["blocks"].append(block)

    return id_, block
    # save_blockchain(id_=user_id, chain=chain)


def create_record(
    user_id: int, block_id: int, content: str, record_id: int | None = None
) -> None:
    """Deprecated: it takes block from chain and adds record to it"""
    chain = load_blockchain(user_id)
    for block in chain["blocks"]:
        if block["index"] == block_id:
            block["records"].sort(key=lambda x: x["timestamp"])

            if record_id != None:
                id_ = record_id
            if len(block["records"]) > 0:
                id_ = block["records"][-1]["index"] + 1
            else:
                id_ = 1
            record = {
                "index": id_,
                "timestamp": datetime.now().timestamp(),
                "content": content,
            }
            block["records"].append(record)
            break

    save_blockchain(user_id, chain)


def create_record_for_block(
    block: dict, content: str, record_id: int | None = None
) -> dict:
    block["records"].sort(key=lambda x: x["timestamp"])

    if record_id != None:
        id_ = record_id
    if len(block["records"]) > 0:
        id_ = block["records"][-1]["index"] + 1
    else:
        id_ = 1
    record = {
        "index": id_,
        "timestamp": datetime.now().timestamp(),
        "content": content,
    }
    block["records"].append(record)
    return block


def add_block_to_chain(block: dict, user_id: int) -> None:
    chain = load_blockchain(user_id)
    chain["blocks"].append(block)
    save_blockchain(id_=user_id, chain=chain)
