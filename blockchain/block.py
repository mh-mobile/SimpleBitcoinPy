import binascii
import hashlib
from time import time
import json
import datetime


class Block:
    def __init__(self, transaction, previous_block_hash):
        self.timestamp = time()
        self.transaction = transaction
        self.previous_block = previous_block_hash

        current = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(current)

        json_block = json.dumps(self.to_dict(
            include_nonce=False), sort_keys=True)
        print('json_block : ', json_block)
        self.nonce = self._compute_nonce_for_pow(json_block)

        current2 = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(current2)

    def _compute_nonce_for_pow(self, message, difficulty=5):
        i = 0
        suffix = '0' * difficulty
        while True:
            nonce = str(i)
            digest = binascii.hexlify(self._get_double_sha256(
                (message + nonce).encode('utf-8'))).decode('ascii')
            if digest.endswith(suffix):
                return nonce
            i += 1

    def _get_double_sha256(self, message):
        return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def to_dict(self):
        d = {
            "timestamp": self.timestamp,
            "transaction": json.dumps(self.transaction),
            "previous_block": self.previous_block,
        }
        return d


class GenesisBlock(Block):
    def __init__(self):
        super().__init__(transaction='AD9B477B42B22CDF18B1335603D07378ACE83561D8398FBFC8DE94196C65D806',
                         previous_block_hash=None)

    def to_dict(self):
        d = {
            'transaction': self.transaction,
            'genesis_block': True,
        }
        return d
