STATE_INIT = 0
STATE_STANBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3

class ServerCore:
    def __init__(self):
        self.server_state = STATE_INIT
        print('Initializing server...')

    def start(self):
        self.server_state = STATE_STANBY

    def join_network(self):
        self.server_state = STATE_CONNECTED_TO_NETWORK

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        print('Shutdown server...')

    def get_my_current_state(self):
        return self.server_state

if __name__ == '__main__':
    core = ServerCore()
    print('state: {}'.format(core.get_my_current_state()))
    core.start()
    print('state: {}'.format(core.get_my_current_state()))
    core.join_network()
    print('state: {}'.format(core.get_my_current_state()))
    core.shutdown()
    print('state: {}'.format(core.get_my_current_state()))
