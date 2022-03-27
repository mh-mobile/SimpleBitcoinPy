from time import time


class TransactionInput:
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index

    def to_dict(self):
        d = {
            'transaction': self.transaction.to_dict(),
            'output_index': self.output_index
        }
        return d


class TransactionOutput:
    def __init__(self, recipient_address, value):
        self.recipient = recipient_address
        self.value = value

    def to_dict(self):
        d = {
            'recipient': self.recipient,
            'value': self.value
        }
        return d


class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time()

    def to_dict(self):
        d = {
            'inputs': list(map(TransactionInput.to_dict, self.inputs)),
            'outputs': list(map(TransactionOutput.to_dict, self.outputs)),
            'timestamp': self.timestamp
        }

        return d

    def is_enough_inputs(self, fee):
        total_in = sum(
            i.transaction.outputs[i.output_index].value for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)
        delta = total_in - total_out
        print('delta: ', delta)
        if delta >= 0:
            return True
        else:
            return False

    def compute_change(self, fee):
        total_in = sum(
            i.transactioin.outputs[i.output_index].value for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)
        delta = total_in - total_out
        return delta


class CoinbaseTransaction(Transaction):
    def __init__(self, recipent_address, value=30):
        self.inputs = []
        self.outputs = [TransactionOutput(recipent_address, value)]
        self.timestamp = time()
        self.timestamp = time()

    def to_dict(self):
        d = {
            'inputs': [],
            'outputs': list(map(TransactionOutput.to_dict, self.outputs)),
            'timestamp': self.timestamp,
            'coinbase_transaction': True
        }
        return d
