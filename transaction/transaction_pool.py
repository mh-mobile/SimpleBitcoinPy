import threading


class TransactionPool:
    def __init__(self):
        print('Initializing TransactionPool...')
        self.transactions = []
        self.lock = threading.Lock()

    def set_new_transaction(self, transaction):
        with self.lock:
            print('set_new_transaction is called', transaction)
            self.transactions.append(transaction)

    def clear_my_transactions(self, index):
        with self.lock:
            if index <= len(self.transactions):
                new_transactions = self.transactions
                del new_transactions[0:index]
                print('transaction is now refreshed ...', new_transactions)
                self.transactions = new_transactions

    def get_stored_transactions(self):
        if len(self.transactions) > 0:
            return self.transactions
        else:
            print("Currently, it seems transaction pool is empty...")
            return []

    def renew_my_transactions(self, transactions):
        with self.lock:
            print('transaction pool will be renewed to ...', transactions)
            self.transactions = transactions

    def get_total_fee_from_tp(self):
        print('get_total_fee_from_tp is called')
        transactions = self.transactions
        result = 0
        for t in transactions:
            checked = self.check_type_of_transaction(t)
            if checked:
                total_in = sum(
                    i['transaction']['outputs'][i['output_index']]['value']
                    for i in t['inputs']
                )
                total_out = sum(o['value'] for o in t['outputs'])
                delta = total_in - total_out
                result += delta

        return result

    def check_type_of_transaction(self, transaction):
        if transaction['t_type'] == 'basic' or transaction['t_type'] == 'coinbase_transaction':
            return True
        else:
            return False
