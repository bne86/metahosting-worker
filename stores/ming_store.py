import ming
from stores.abstract_kv_store import AbstractKVStore

class MingStore(AbstractKVStore):

    def initialize_collection(self):
        client = ming.create_datastore(self.get_property('url')).conn
        return client[self.get_property('database')][self.get_property(
            'collection')]
