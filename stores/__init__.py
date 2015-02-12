from config_manager import get_configuration
from stores.mongo_store import MongoStore


def get_stores():
    config = get_configuration('persistency')

    configuration = dict()
    configuration['url'] = 'mongodb://%s:%s/metahosting' % (config['host'],
                                                            config['port'])
    configuration['database'] = 'metahosting'

    configuration['collection'] = 'types'
    type_store = MongoStore(config=configuration)

    configuration['collection'] = 'instances'
    instance_store = MongoStore(config=configuration)
    return type_store, instance_store
