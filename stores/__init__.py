import logging
import os
from stores.ming_store import MingStore
from stores.dict_store import Store
HOST = 'DB_PORT_27017_TCP_ADDR'
PORT = 'DB_PORT_27017_TCP_PORT'

type_store = Store()
instance_store = Store()

if HOST not in os.environ or PORT not in os.environ:
    logging.warning('Using default store connection details. Set [%s, %s].',
                    HOST, PORT)
else:
    config = dict()
    config['url'] = 'mongodb://%s:%s/metahosting' % (
        os.getenv(HOST, 'localhost'),
        os.getenv(PORT, '27017'))
    config['database'] = 'metahosting'

    config['collection'] = 'types'
    type_store = MingStore(config=config)

    config['collection'] = 'instances'
    instance_store = MingStore(config=config)
