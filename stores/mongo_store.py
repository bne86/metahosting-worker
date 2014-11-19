from pymongo import MongoClient
from abstract_kv_store import AbstractKVStore


class MongoStore(AbstractKVStore):

    def initialize_collection(self):
        client = MongoClient(self.get_property('url'))
        return client[self.get_property('database')][self.get_property(
            'collection')]