from queue_manager import qm

from facade import facade_listener

# this file might become redundant: facade listener could register itself
# in facade file

# also worker(s) will register themselves

qm.subscribe('info', facade_listener)


from worker import init
init()

# qm.publish('service_a', 'Create new1')
# qm.publish('service_a', 'Create new2')
# qm.publish('service_b', 'Create new3')
