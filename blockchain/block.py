from time import time
import json


class Block:
    def __init__(self, transaction, previous_block_hash):
        self.timestamp = time()
        self.transaction = transaction
        self.previous_block = previous_block_hash

    def to_dict(self):
        d = {
            "timestamp": self.timestamp,
            "transaction": json.dumps(self.transaction),
            "previous_block": self.previous_block,
        }
        return d
