# from message_manager import MessageManager

PING_INTERVAL = 1800

class ConnectionManager:
    def __init__(self, host, my_port):
        print('Initializing ConnectionManager...')
        self.host = host
        self.port = my_port
        self.core_node_set = set()
        self.__add_peer((host, my_port))
        # self.mm = MessageManager()

    def start(self):
        pass

    def join_network(self):
        pass

    def send_msg(self):
        pass

    def send_msg_to_all_peer(self):
        pass

    def connection_close(self):
        pass

    def connection_close(self):
        pass

    def __handle_message(self):
        pass

    def __add_peer(self, peer):
        print('add_peer...')

    def __remove_peer(self):
        pass

    def __check_peers_connection(self):
        pass

if __name__ == '__main__':
    manager = ConnectionManager("127.0.0.1", 8080)
    print("host: {host}, port: {port}".format(host=manager.host, port=manager.port))