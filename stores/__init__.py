import ConfigParser
import logging
import os
from stores.ming_store import MingStore
from stores.dict_store import Store


HOST = 'DB_PORT_27017_TCP_ADDR'
PORT = 'DB_PORT_27017_TCP_PORT'
DICT_STORE = False

# if ENV not set in a default way, try to get other
# variables or a configuration file.
if HOST not in os.environ or PORT not in os.environ:
    # maybe the environment is different, keep it configurable
    envvars = ConfigParser.ConfigParser()
    try:
        envvars.readfp(open('envvars.ini'))
        HOST = envvars.get('persistency', 'HOST_VARIABLE')
        PORT = envvars.get('persistency', 'PORT_VARIABLE')
    except IOError as err:
        logging.debug('Option file for environment variables not found.')
        logging.error(err)
    except ConfigParser.NoOptionError as err:
        logging.debug('Options not found in environment variable option file.')
        logging.error(err)

# initialize with defaults
host = 'localhost'
port = 27017

# if new ENVs still not set, we should look for a configuration file,
# otherwise configure the storage
if HOST not in os.environ or PORT not in os.environ:
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open('config.ini'))
        host = config.get('persistency', 'host')
        port = int(config.get('persistency', 'port'))
    except IOError or ConfigParser.NoOptionError as err:
        logging.debug('Establishing persistency connection not possible '
                      'because both env and config are not valid,'
                      'using memory store')
        # perhaps better to just die?
        logging.error(err)
        DICT_STORE = True
else:
    host = os.getenv(HOST, 'localhost')
    port = int(os.getenv(PORT, 27017))


if DICT_STORE:
    type_store = Store()
    instance_store = Store()
else:
    logging.debug('Connecting to store on %s:%s', host, port)
    configuration = dict()
    configuration['url'] = 'mongodb://%s:%s/metahosting' % (host, port)
    configuration['database'] = 'metahosting'

    configuration['collection'] = 'types'
    type_store = MingStore(config=configuration)

    configuration['collection'] = 'instances'
    instance_store = MingStore(config=configuration)
