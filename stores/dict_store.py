class Store(object):

    def __init__(self):
        self.store = dict()

    def update(self, name, value):
        self.store[name] = value

    def get(self, name):
        if name not in self.store:
            return None
        return self.store[name].copy()

    def get_all(self):
        return self.store.copy()