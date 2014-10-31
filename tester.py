import time
from facade import get_all_instances, get_instance_types, create_instance

from store_updater import init as updater_init
updater_init()

from worker import stop, init as worker_init
worker_init()

if __name__ == "__main__":
    print('Starting testing...')
    types = get_instance_types()
    print('Instance types:\n')
    for r_type in types:
        print('\t%s\n' % r_type)

    print('\nSubmitting creation request\n')
    i = create_instance('service_a')
    print('Instance:\n%s' % i)

    print('\nSubmitting creation request\n')
    i = create_instance('service_a')
    print('Instance:\n%s' % i)

    print('All instances:')
    instances = get_all_instances()
    for k, v in instances.iteritems():
        print('%s -- %s' % (k, v))

    print('..>Waiting<..')
    time.sleep(5)
    print('All instances:')
    instances = get_all_instances()
    for k, v in instances.iteritems():
        print('%s -- %s' % (k, v))
    stop()
