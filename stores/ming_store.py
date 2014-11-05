import ming


class MingStore(object):

    def __init__(self, database, collection):
        # equivalent to MongoClient('mongodb://localhost:27017/')
        client = ming.create_datastore('mim://').conn
        self.collection = client[database][collection]

    def update(self, name, value):
        self.collection.insert({'name': name, 'value': value})

    def get(self, name):
        doc = self.collection.find_one({'name': name})
        return doc

    def get_all(self):
        return self.collection.find().all()
