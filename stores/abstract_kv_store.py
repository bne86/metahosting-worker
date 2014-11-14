from abc import ABCMeta, abstractproperty


class AbstractKVStore(object):
    __metaclass__ = ABCMeta

    def update(self, name, value):
        self.collection.insert({'name': name, 'value': value})

    def get(self, name):
        return self.collection.find_one({'name': name})

    def get_all(self):
        return list(self.collection.find())
