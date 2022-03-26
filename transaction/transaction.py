class TransactionOutput:
    def __init__(self, recipient_address, value):
        self.recipient = recipient_address
        self.value = value


class TransactionInput:
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index


class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs


class CoinbaseTransaction(Transaction):
    def __init__(self, recipent_address, value=30):
        self.inputs = []
        self.outputs = [TransactionOutput(recipent_address, value)]
