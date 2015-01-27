import ConfigParser
import logging
import os
from stores.ming_store import MingStore
from stores.dict_store import Store
from stores.mongo_store import MongoStore

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 27017


DICT_STORE = False
envvars = ConfigParser.SafeConfigParser(
    {'HOST_VARIABLE': 'DB_PORT_27017_TCP_ADDR',
     'PORT_VARIABLE': 'DB_PORT_27017_TCP_PORT'})
envvars.read('envvars.ini')
HOST = envvars.get('persistency', 'HOST_VARIABLE')
PORT = envvars.get('persistency', 'PORT_VARIABLE')

if HOST not in os.environ or PORT not in os.environ:
    config = ConfigParser.SafeConfigParser(
        {'host': DEFAULT_HOST, 'port': DEFAULT_PORT}
    )
    config.read('config.ini')
    host = config.get('persistency', 'host')
    port = int(config.get('persistency', 'port'))
else:
    host = os.getenv(HOST, 'localhost')
    port = int(os.getenv(PORT, 27017))

logging.debug('Connecting to store on %s:%s', host, port)
configuration = dict()
configuration['url'] = 'mongodb://%s:%s/metahosting' % (host, port)
configuration['database'] = 'metahosting'

configuration['collection'] = 'types'
type_store = MongoStore(config=configuration)

configuration['collection'] = 'instances'
instance_store = MongoStore(config=configuration)
