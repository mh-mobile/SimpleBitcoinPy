import threading


class MessageStore:

    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    def add(self, msg):
        with self.lock:
            self.list.append(msg)

    def remove(self, msg):
        with self.lock:
            toBeRemoved = None
            for m in self.list:
                if msg == m:
                    toBeRemoved = m
                    break

            if not toBeRemoved:
                return

            self.list.remove(toBeRemoved)

    def overwrite(self, new_list):
        with self.lock:
            self.list = new_list

    def get_list(self):
        if len(self.list) > 0:
            return self.list
        else:
            return None

    def get_length(self):
        return len(self.list)

    def has_this_msg(self, msg):
        for m in self.list:
            if m == msg:
                return True

        return False
