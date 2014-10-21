from queue_manager import qm

from facade import init as facade_init, get_all_instances, get_instance_types, \
    create_instance

facade_init(qm)

from worker import init as worker_init, stop

worker_init(qm)


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

    print('All instances:\n')
    instances = get_all_instances()
    for k, v in instances.iteritems():
        print('%s -- %s' % (k, v))

    stop()
    print('End')