import ming
from abstract_kv_store import AbstractKVStore


class MingStore(AbstractKVStore):
    def __init__(self, database, collection):
        # equivalent to MongoClient('mongodb://localhost:27017/')
        client = ming.create_datastore('mim://').conn
        self.collection = client[database][collection]
