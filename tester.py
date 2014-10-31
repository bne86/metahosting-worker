from queue_manager import subscribe, send_message
import time
from facade import init as facade_init, get_all_instances, get_instance_types,\
    create_instance

print('Initializing facade')
facade_init(subscribe_method=subscribe, send_message_method=send_message)

from worker import init as worker_init, stop
print('Initializing worker')
worker_init(subscribe_method=subscribe, send_message_method=send_message)


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
