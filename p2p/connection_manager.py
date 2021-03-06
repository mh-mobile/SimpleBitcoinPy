from email import message
import pickle
import threading
from .message_manager import ERR_PROTOCOL_UNMATCH, ERR_VERSION_UNMATCH, MSG_ADD, MSG_ADD_AS_EDGE, MSG_CORE_LIST, MSG_PING, MSG_REMOVE, MSG_REMOVE_EDGE, MSG_REQUEST_CORE_LIST, OK_WITH_PAYLOAD, OK_WITHOUT_PAYLOAD, MessageManager
from concurrent.futures import ThreadPoolExecutor
from .core_node_list import CoreNodeList
from .edge_node_list import EdgeNodeList
import socket

PING_INTERVAL = 10


class ConnectionManager:
    def __init__(self, host, my_port, callback):
        print('Initializing ConnectionManager...')
        self.host = host
        self.port = my_port
        self.my_c_host = None
        self.my_c_port = None
        self.core_node_set = CoreNodeList()
        self.edge_node_set = EdgeNodeList()
        self.__add_peer((host, my_port))
        self.mm = MessageManager()
        self.callback = callback

    def start(self):
        t = threading.Thread(target=self.__wait_for_access)
        t.start()

        self.ping_timer = threading.Timer(
            PING_INTERVAL, self.__check_peers_connection)
        self.ping_timer.start()

    def join_network(self, host, port):
        self.my_c_host = host
        self.my_c_port = port
        self.__connect_to_P2PNW(host, port)

    def __connect_to_P2PNW(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        msg = self.mm.build(MSG_ADD, self.port)
        s.sendall(msg.encode('utf-8'))
        s.close()

    def send_msg(self, peer, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer))
            s.sendall(msg.encode('utf-8'))
            s.close()
        except OSError:
            print('Connection failed for peer : ', peer)
            self.__remove_peer(peer)

    def send_msg_to_all_peer(self, msg):
        print('send_msg_to_all_peer was called!')
        for peer in self.core_node_set.get_list():
            if peer != (self.host, self.port):
                print('message will be sent to ... ', peer)
                self.send_msg(peer, msg)

    def send_msg_to_all_edge(self, msg):
        print('send_msg_to_all_edge was called!')
        for peer in self.edge_node_set.get_list():
            if peer != (self.host, self.port):
                print('message will be sent to ... ', peer)
                self.send_msg(peer, msg)

    def connection_close(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket.close()
        s.close()

        self.ping_timer.cancel()
        if self.my_c_host is not None:
            msg = self.mm.build(MSG_REMOVE, self.port)
            self.send_msg((self.my_c_host, self.my_c_port), msg)

    def __handle_message(self, params):
        soc, addr, data_sum = params

        while True:
            data = soc.recv(1024)
            data_sum = data_sum + data.decode('utf-8')

            if not data:
                break

        if not data_sum:
            return

        result, reason, cmd, peer_port, payload = self.mm.parse(data_sum)
        print(result, reason, cmd, peer_port, payload)
        status = (result, reason)

        if status == ('error', ERR_PROTOCOL_UNMATCH):
            print('Error: Protocol name is not matched')
            return
        elif status == ('error', ERR_VERSION_UNMATCH):
            print('Error: Protocol version is not matched')
            return
        elif status == ('ok', OK_WITHOUT_PAYLOAD):
            if cmd == MSG_ADD:
                print('Add node request was received!!')
                self.__add_peer((addr[0], peer_port))
                if (addr[0], peer_port) == (self.host, self.port):
                    return
                else:
                    cl = pickle.dumps(
                        self.core_node_set.get_list(), 0).decode()
                    msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                    self.send_msg_to_all_peer(msg)
                    self.send_msg_to_all_edge(msg)
            elif cmd == MSG_REMOVE:
                print('REMOVE request was received!! from', addr[0], peer_port)
                self.__remove_peer((addr[0], peer_port))
                cl = pickle.dumps(self.core_node_set.get_list(), 0).decode()
                msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                self.send_msg_to_all_peer(msg)
                self.send_msg_to_all_edge(msg)
            elif cmd == MSG_PING:
                return
            elif cmd == MSG_REQUEST_CORE_LIST:
                print('List for Core nodes was requested!!')
                cl = pickle.dumps(self.core_node_set.get_list(), 0).decode()
                msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                self.send_msg((addr[0], peer_port), msg)
            elif cmd == MSG_ADD_AS_EDGE:
                print('ADD request for Edge node was received!!')
                self.__add_edge_node((addr[0], peer_port))
                cl = pickle.dumps(self.core_node_set.get_list(), 0).decode()
                msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                self.send_msg((addr[0], peer_port), msg)
            elif cmd == MSG_REMOVE_EDGE:
                self.__remove_edge_node((addr[0], peer_port))
            else:
                print('recieved unknown command', cmd)
                is_core = self.__is_in_core_set((addr[0], peer_port))
                self.callback((result, reason, cmd, peer_port,
                              payload), is_core, (addr[0], peer_port))
                return
        elif status == ('ok', OK_WITH_PAYLOAD):
            if cmd == MSG_CORE_LIST:
                print('Refresh the core node list...')
                new_core_set = pickle.loads(payload.encode('utf8'))
                print('latest core node list: ', new_core_set)
                self.core_node_set = CoreNodeList()
                self.core_node_set.overwrite(new_core_set)
            else:
                print('received unknown command', cmd)
                is_core = self.__is_in_core_set((addr[0], peer_port))
                self.callback(
                    (result, reason, cmd, peer_port, payload), is_core, None)
                return
        else:
            print('Unexpected status', status)

    def __add_peer(self, peer):
        print('add_peer: ', peer)
        self.core_node_set.add((peer))

    def __remove_peer(self, peer):
        self.core_node_set.remove(peer)

    def __check_peers_connection(self):
        """
        ?????????????????????Core????????????????????????????????????????????????????????????????????????????????????????????????
        ????????????????????????????????????????????????
        """
        print('check_peers_connection was called')
        current_core_list = self.core_node_set.get_list()
        changed = False
        dead_c_node_set = list(
            filter(lambda p: not self.__is_alive(p), current_core_list))

        if dead_c_node_set:
            changed = True
            print('Removing ', dead_c_node_set)
            current_core_list = current_core_list - set(dead_c_node_set)
            self.core_node_set.overwrite(current_core_list)

        current_core_list = self.core_node_set.get_list()
        print('current core node list:', current_core_list)

        if changed:
            cl = pickle.dumps(current_core_list, 0).decode()
            msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
            self.send_msg_to_all_peer(msg)

        self.ping_timer = threading.Timer(
            PING_INTERVAL, self.__check_peers_connection)
        self.ping_timer.start()

    def __is_alive(self, target):
        """
        ?????????????????????????????????????????????

        param:
            target : ?????????????????????????????????????????????????????????????????????????????????
                    ???IP?????????????????????????????????
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target))
            msg_type = MSG_PING
            msg = self.mm.build(msg_type)
            s.sendall(msg.encode('utf-8'))
            s.close()
            return True
        except OSError:
            return False

    def __wait_for_access(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(0)

        executor = ThreadPoolExecutor(max_workers=10)

        while True:
            try:
                print('Wating for the connection ....')
                soc, addr = self.socket.accept()

                print('Connected by ...', addr)
                data_sum = ''

                params = (soc, addr, data_sum)
                executor.submit(self.__handle_message, params)
            except socket.error:
                break

    def __add_edge_node(self, edge):
        self.edge_node_set.add((edge))

    def __remove_edge_node(self, edge):
        self.edge_node_set.remove(edge)

    def get_message_text(self, msg_type, payload=None):
        msgtxt = self.mm.build(msg_type, self.port, payload)
        print('generated_msg: ', msgtxt)
        return msgtxt

    def __is_in_core_set(self, peer):
        return self.core_node_set.has_this_peer(peer)


if __name__ == '__main__':
    manager = ConnectionManager("127.0.0.1", 8080)
    print("host: {host}, port: {port}".format(
        host=manager.host, port=manager.port))
