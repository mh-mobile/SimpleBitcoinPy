import threading


class EdgeNodeList:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = set()

    def add(self, edge):
        with self.lock:
            print('Adding edge: ', edge)
            self.list.add((edge))
            print('Current Edge List: ', self.list)

    def remove(self, edge):
        if edge in self.list:
            print('Removing edge: ', edge)
            self.list.remove(edge)
            print('Current Edge list: ', self.list)

    def overwrite(self, new_list):
        with self.lock:
            print('edge node list will be going to overwrite')
            self.list = new_list
            print('Current Edge list: ', self.list)

    def get_list(self):
        return self.list
