from abc import ABCMeta, abstractmethod


class AbstractKVStore(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.settings = dict()
        if 'config' in kwargs:
            self.config_update(kwargs['config'])
        else:
            # defaults?
            self.collection = self.initialize_collection()

    def update(self, name, value):
        self.collection.insert({'name': name, 'value': value})

    def get(self, name):
        return self.collection.find_one({'name': name})

    def get_all(self):
        return list(self.collection.find())

    def config_update(self, settings):
        for k, v in settings.iteritems():
            self.set_property(k, v)
        self.collection = self.initialize_collection()

    @abstractmethod
    def initialize_collection(self):
        pass

    def set_property(self, key, value):
        self.settings[key] = value

    def get_property(self, key):
        if key in self.settings:
            return self.settings[key]
        else:
            return None