import signal
from time import sleep
import json

from core.client_core import ClientCore
from p2p.message_manager import MSG_ENHANCED, MSG_NEW_TRANSACTION

my_p2p_client = None


def signal_handler(signal, frame):
    shutdown_client()


def shutdown_client():
    global my_p2p_client
    my_p2p_client.shutdown()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_p2p_client
    my_p2p_client = ClientCore(50097, '192.168.65.3', 50082)
    my_p2p_client.start()

    sleep(10)

    # message = {
    #     'from': 'hoge',
    #     'to': 'fuga',
    #     'message': 'test'
    # }

    transaction = {
        'sender': 'test51',
        'recipient': 'test21',
        'value': 10
    }

    my_p2p_client.send_message_to_my_core_node(
        MSG_NEW_TRANSACTION, json.dumps(transaction))

    transaction2 = {
        'sender': 'test81',
        'recipent': 'test91',
        'value': 200
    }

    my_p2p_client.send_message_to_my_core_node(
        MSG_NEW_TRANSACTION, json.dumps(transaction2))

    sleep(10)

    transaction3 = {
        'sender': 'test210',
        'recipient': 'test30',
        'value': 80
    }

    my_p2p_client.send_message_to_my_core_node(
        MSG_NEW_TRANSACTION, json.dumps(transaction3))


if __name__ == '__main__':
    main()
