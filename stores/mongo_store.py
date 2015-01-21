from pymongo import MongoClient
from stores.abstract_kv_store import AbstractKVStore
import logging


class MongoStore(AbstractKVStore):

    def initialize_collection(self):
        logging.warning('Use MingStore to connect to mongodb')
        client = MongoClient(self.get_property('url'))
        return client[self.get_property('database')][self.get_property(
            'collection')]
