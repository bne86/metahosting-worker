import ming
from abstract_kv_store import AbstractKVStore


class MingStore(AbstractKVStore):
    def __init__(self, database, collection):
        client = ming.create_datastore('mim://').conn
        self.collection = client[database][collection]
