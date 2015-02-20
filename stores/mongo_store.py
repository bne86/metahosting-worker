from pymongo import MongoClient
from stores.abstract_kv_store import AbstractKVStore


class MongoStore(AbstractKVStore):
    def initialize_collection(self):
        client = MongoClient(self.get_property('url'))
        return client[self.get_property('database')][self.get_property(
            'collection')]

    def update(self, name, value):
        self.collection.update(spec={'name': name},
                               document={'name': name, 'value': value},
                               upsert=True)
