import pickle
import socket
import threading
import json
import copy

from p2p.connection_manager import ConnectionManager
from p2p.message_manager import MSG_ENHANCED, MSG_NEW_TRANSACTION, MSG_NEW_BLOCK, MSG_REQUEST_FULL_CHAIN, RSP_FULL_CHAIN
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.my_protocol_message_store import MessageStore
from blockchain.block_builder import BlockBuilder
from blockchain.blockchain_manager import BlockchainManager
from transaction.transaction_pool import TransactionPool
from transaction.uxto_manager import UTXOManager
from transaction.transaction import CoinbaseTransaction
from utils.key_manager import KeyManager
from utils.rsa_util import RSAUtil


STATE_INIT = 0
STATE_STANBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


CHECK_INTERVAL = 10


class ServerCore:
    def __init__(self, my_port=50082, core_node_host=None,
                 core_node_port=None, pass_phrase=None):
        self.server_state = STATE_INIT
        print('Initializing server...')
        self.my_ip = self.__get__myip()
        print('Server IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(
            self.my_ip, self.my_port, self.__handle_message)
        self.mpmh = MyProtocolMessageHandler()
        self.core_node_host = core_node_host
        self.core_node_port = core_node_port
        self.npm_store = MessageStore()
        self.bb = BlockBuilder()
        self.is_bb_runing = False
        self.flag_stop_block_build = True
        my_genesis_block = self.bb.generate_genesis_block()
        self.bm = BlockchainManager(my_genesis_block.to_dict())
        self.prev_block_hash = self.bm.get_hash(my_genesis_block.to_dict())
        self.tp = TransactionPool()
        self.km = KeyManager(None, pass_phrase)
        self.um = UTXOManager(self.km.my_address())
        self.rsa_util = RSAUtil()

    def start(self):
        self.server_state = STATE_STANBY
        self.cm.start()

        self.bb_timer = threading.Timer(
            CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def join_network(self):
        if self.core_node_host is not None:
            self.server_state = STATE_CONNECTED_TO_NETWORK
            self.cm.join_network(self.core_node_host, self.core_node_port)
        else:
            print('This server is running as Genesis Core Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        print('Shutdown server...')
        self.cm.connection_close()

    def get_my_current_state(self):
        return self.server_state

    def __get__myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]

    def __handle_message(self, msg, is_core, peer=None):
        if peer is not None:
            if msg[2] == MSG_REQUEST_FULL_CHAIN:
                print('Send our latest blockchain for reply to : ', peer)
                mychain = self.bm.get_my_blockchain()
                chain_data = pickle.dumps(mychain, 0).decode()
                new_message = self.cm.get_message_text(
                    RSP_FULL_CHAIN, chain_data)
                self.cm.send_msg(peer, new_message)
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                new_transaction = json.loads(msg[4])
                print('received new_transaction', new_transaction)
                is_sbc_t, _ = self.um.is_sbc_transaction(new_transaction)
                current_transactions = self.tp.get_stored_transactions()
                if new_transaction in current_transactions:
                    print('this is already pooled transaction: ', new_transaction)
                    return

                    if not is_sbc_t:
                        print('this is not SimpleBitcon transaction:',
                              new_transaction)
                    else:
                        if self.bm.get_my_chain_length() != 1:
                            checked = self._check_availability_of_transaction(
                                new_transaction)
                            if not checked:
                                print('Transaction Verification Error')
                                return

                    self.tp.set_new_transaction(new_transaction)

                    if not is_core:
                        self.tp.set_new_transaction(new_transaction)
                        new_message = self.cm.get_message_text(
                            MSG_NEW_TRANSACTION, json.dumps(new_transaction))
                        self.cm.send_msg_to_all_peer(new_message)

                else:
                    if not is_sbc_t:
                        print('this is not SimpleBitcon transaction: ',
                              new_transaction)
                    else:
                        if self.bm.get_my_chain_length() != 1:
                            checked = self._check_availability_of_transaction(
                                new_transaction)
                            if not checked:
                                print('Transaction Verification Error')
                                return

                    self.tp.set_new_transaction(new_transaction)

                    if not is_core:
                        new_message = self.cm.get_message_text(
                            MSG_NEW_TRANSACTION, json.dumps(new_transaction))
                        self.cm.send_msg_to_all_peer(new_message)
            elif msg[2] == MSG_NEW_BLOCK:
                if not is_core:
                    print('block received from unknown')
                    return

                new_block = json.loads(msg[4])
                print('new_block: ', new_block)
                if self.bm.is_valid_block(self.prev_block_hash, new_block):

                    block_check_result = self.check_transactions_in_new_block(
                        new_block)
                    print('block_check_result: ', block_check_result)
                    if block_check_result is not True:
                        print('previous block hash is ok. but still not acceptable.')
                        self.get_all_chains_for_resolve_conflict()
                        return

                    if self.is_bb_running:
                        self.flag_stop_block_build = True
                    self.prev_block_hash = self.bm.get_hash(new_block)
                    self.bm.set_new_block(new_block)
                else:
                    self.get_all_chains_for_resolve_conflict()

            elif msg[2] == RSP_FULL_CHAIN:
                if not is_core:
                    print('blockchain received from unknown')
                    return

                new_block_chain = pickle.loads(msg[4].encode('utf8'))
                print(new_block_chain)

                result, pool_4_orphan_blocks = self.bm.resolve_conflicts(
                    new_block_chain)
                print('blockchain received from central')
                if result is not None:
                    self.prev_block_hash = result
                    if len(pool_4_orphan_blocks) != 0:
                        new_transactions = self.bm.get_transactions_from_orphan_blocks(
                            pool_4_orphan_blocks)
                        for t in new_transactions:
                            self.tp.set_new_transaction(t)
                else:
                    print('Received blockchain is useless')

            elif msg[2] == MSG_ENHANCED:
                print('received enhanced message', msg[4])
                has_same = self.npm_store.has_this_msg(msg[4])
                if has_same is not True:
                    self.npm_store.add(msg[4])
                    self.mpmh.handle_message(msg[4], self.__core_api)

    def __core_api(self, request, message):

        msg_type = MSG_ENHANCED

        if request == 'send_message_to_all_peer':
            new_message = self.cm.get_message_text(msg_type, message)
            self.cm.send_msg_to_all_peer(new_message)
            return 'ok'
        elif request == 'send_message_to_all_edge':
            new_message = self.cm.get_message_text(msg_type, message)
            self.cm.send_msg_to_all_edge(new_message)
            return 'ok'
        elif request == 'api_type':
            return 'server_core_api'

    def __generate_block_with_tp(self):
        print('Thread for generate_block_with_tp started!')
        while self.flag_stop_block_build is not True:
            self.is_bb_runing = True
            prev_hash = copy.copy(self.prev_block_hash)
            result = self.tp.get_stored_transactions()
            print('generate_block_with_tp called!')
            if len(result) == 0:
                print('Transaction Pool is empty ...')
                break

            new_tp = self.bm.remove_useless_transaction(result)
            self.tp.renew_my_transactions(new_tp)
            if len(new_tp) == 0:
                break

            total_fee = self.tp.get_total_fee_from_tp()
            total_fee += 30

            my_coinbase_t = CoinbaseTransaction(
                self.km.my_address(), total_fee)
            transactions_4_block = copy.deepcopy(new_tp)
            transactions_4_block.insert(0, my_coinbase_t.to_dict())

            new_block = self.bb.generate_new_block(
                transactions_4_block, prev_hash)

            if new_block.to_dic()['previous_block'] == self.prev_block_hash:
                self.bm.set_new_block(new_block.to_dict())
                self.prev_block_hash = self.bm.get_hash(new_block.to_dict())

                msg_new_block = self.cm.get_message_text(
                    MSG_NEW_BLOCK, json.dumps(new_block.to_dict()))
                self.cm.send_msg_to_all_peer(msg_new_block)

                index = len(result)
                self.tp.clear_my_transactions(index)
                break
            else:
                print('Bad block. It seems someone already with the PoW.')
                break

        print('Current Blockchain is ...', self.bm.chain)
        print('Current prev_block_hash is ... ', self.prev_block_hash)

        self.flag_stop_block_build = False
        self.is_bb_running = False

        self.bb_timer = threading.Timer(
            CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def get_all_chains_for_resolve_conflict(self):
        print('get_all_chains_for_resolve_conflict called')
        new_message = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
        self.cm.send_msg_to_all_peer(new_message)

    def _check_availability_of_transaction(self, transaction):
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(
            transaction)

        if v_result is not True:
            print('signature verification error on new transaction')
            return False

        for used_o in used_outputs:
            print('used_o', used_o)
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            tp_v_result = self.bm.has_this_output_in_my_tp(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)

            if bm_v_result:
                print('This TransactionOutput is already used', used_o)
                return False
            if tp_v_result:
                print(
                    'This TransactionOutput is already stored in the TransactionPool', used_o)
                return False
            if bm_v_result2 is not True:
                print('This TransactionOutput is unknown', used_o)

        return True

    def get_total_fee_on_block(self, block):
        print('get_total_fee_on_block is called')
        transactions = block['transactions']
        result = 0
        for t in transactions:
            t = json.loads(t)
            is_sbc_t, t_type = self.um.is_sbc_transaction(t)
            if t_type == 'basic':
                total_in = sum(
                    i['transaction']['outputs'][i['output_index']]['value']
                    for i in t['inputs']
                )
                total_out = sum(o['value'] for o in t['outputs'])
                delta = total_in - total_out
                result += delta

        return result

    def check_transactions_in_new_block(self, block):
        fee_for_block = self.get_total_fee_on_block(block)
        fee_for_block += 30
        print('fee_for_block: ', fee_for_block)

        transactions = block['transactions']
        counter = 0

        for t in transactions:
            t = json.loads(t)
            is_sbc_t, t_type = self.um.is_sbc_transaction(t)
            if is_sbc_t:
                if t_type == 'basic':
                    if self._check_availability_of_transaction_in_block(t) is not True:
                        print('Bad Block. Having invalid Transaction')
                        return False
            elif t_type == 'coinbase_transaction':
                if counter != 0:
                    print('Coinbase Transaction is only for BlockBuilder')
                    return False
                else:
                    insentive = t['outputs'][0]['value']
                    print('insentive', insentive)
                    counter += 1
                    if insentive != fee_for_block:
                        print(
                            'Invalid value in fee for CoinbaseTransaction', insentive)
                        return False

        print('ok. this block is acceptable.')
        return True

    def _check_availability_of_transaction_in_block(self, transaction):
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(
            transaction)
        if v_result is not True:
            print('signature verification error on new transaction')
            return False

        print('used_outputs: ', used_outputs)

        for used_o in used_outputs:
            print('used_o: ', used_o)
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)
            if bm_v_result2 is not True:
                print('This TransactionOutput is unknown', used_o)
                return False
            if bm_v_result:
                print('This TransactionOutput is alread used', used_o)
                return False

        return True


if __name__ == '__main__':
    core = ServerCore()
    print('state: {}'.format(core.get_my_current_state()))
    core.start()
    print('state: {}'.format(core.get_my_current_state()))
    core.join_network()
    print('state: {}'.format(core.get_my_current_state()))
    core.shutdown()
    print('state: {}'.format(core.get_my_current_state()))
