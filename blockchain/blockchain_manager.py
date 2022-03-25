import threading


class BlockchianManager:
    def __init__(self):
        print('Initializaing BlockchainManager...')
        self.chain = []
        self.lock = threading.Lock()

    def set_new_block(self, block):
        with self.lock:
            self.chain.append(block)
