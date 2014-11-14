from pymongo import MongoClient
from abstract_kv_store import AbstractKVStore


class MongoStore(AbstractKVStore):
    def __init__(self, url, database, collection):
        client = MongoClient(url)
        self.collection = client[database][collection]
