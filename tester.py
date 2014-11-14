import ConfigParser
import importlib
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)

from facade import get_all_instances, get_instance_types, create_instance

from store_updater import init as updater_init
updater_init()

# settings = ConfigParser.ConfigParser()
# settings.readfp(open('config.ini'))
# worker = importlib.import_module(settings.get('worker', 'backend'))
# worker.init()

if __name__ == "__main__":
    logging.debug('Starting testing...')
    types = get_instance_types()
    logging.debug('Instance types:')
    for r_type in types:
        logging.debug('%s', r_type)

    logging.debug('Submitting creation request')
    i = create_instance('service_a')
    logging.debug('Instance: %s', i)

    logging.debug('Submitting creation request')
    i = create_instance('service_a')
    logging.debug('Instance: %s', i)

    logging.debug('All instances:')
    instances = get_all_instances()
    for k, v in instances.iteritems():
        logging.debug('%s -- %s', k, v)

    logging.debug('..>Waiting<..')
    time.sleep(5)
    logging.debug('All instances:')
    instances = get_all_instances()
    for k, v in instances.iteritems():
        logging.debug('%s -- %s', k, v)