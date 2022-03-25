import socket

from p2p.connection_manager import ConnectionManager
from p2p.message_manager import MSG_ENHANCED, MSG_NEW_TRANSACTION, MSG_NEW_BLOCK, RSP_FULL_CHAIN
from p2p.my_protocol_message_handler import MyProtocolMessageHandler

STATE_INIT = 0
STATE_STANBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


class ServerCore:
    def __init__(self, my_port=50082, core_node_host=None,
                 core_node_port=None):
        self.server_state = STATE_INIT
        print('Initializing server...')
        self.my_ip = self.__get__myip()
        print('Server IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(
            self.my_ip, self.my_port, self.__handle_mesasge)
        self.mpmh = MyProtocolMessageHandler()
        self.core_node_host = core_node_host
        self.core_node_port = core_node_port

    def start(self):
        self.server_state = STATE_STANBY
        self.cm.start()

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

    def __handle_mesasge(self, msg, peer=None):
        if peer is not None:
            print('Send our latest blockchain for reply to : ', peer)
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                pass
            elif msg[2] == MSG_NEW_BLOCK:
                pass
            elif msg[2] == RSP_FULL_CHAIN:
                pass
            elif msg[2] == MSG_ENHANCED:
                self.mpmh.handle_message(msg[4])


if __name__ == '__main__':
    core = ServerCore()
    print('state: {}'.format(core.get_my_current_state()))
    core.start()
    print('state: {}'.format(core.get_my_current_state()))
    core.join_network()
    print('state: {}'.format(core.get_my_current_state()))
    core.shutdown()
    print('state: {}'.format(core.get_my_current_state()))
