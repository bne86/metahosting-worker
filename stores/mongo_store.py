from pymongo import MongoClient
from stores.abstract_kv_store import AbstractKVStore
import logging


class MongoStore(AbstractKVStore):
    def initialize_collection(self):
        logging.warning('Use MingStore to connect to mongodb')
        client = MongoClient(self.get_property('url'))
        return client[self.get_property('database')][self.get_property(
            'collection')]

    def update(self, name, value):
        # fantastic job Ming, it is called either document or updates
        # depending on the backend (mim or mongo). thx.
        self.collection.update(spec={'name': name},
                               document={'name': name, 'value': value},
                               upsert=True)
