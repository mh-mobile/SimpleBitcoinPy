from transaction.transaction import Transaction
from transaction.transaction import TransactionInput
from transaction.transaction import TransactionOutput
from transaction.transaction import CoinbaseTransaction


def main():
    t1 = CoinbaseTransaction('Itsuki_pubkey')

    print(t1.to_dict())
    print(t1.is_enough_inputs(0))

    t2 = Transaction(
        [TransactionInput(t1, 0)],
        [
            TransactionOutput('Umika_pubkey', 10.0),
            TransactionOutput('Itsuki_pubkey', 20.0)
        ]
    )

    print(t2.to_dict())
    print(t2.is_enough_inputs(0))


if __name__ == '__main__':
    main()
