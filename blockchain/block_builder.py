from .block import Block


class BlockBuilder:
    def __init__(self):
        print('Initializaing BlockBuilder...')
        pass

    def generate_new_block(self, transaction, previous_block_hash):
        new_block = Block(transaction, previous_block_hash)
        return new_block
