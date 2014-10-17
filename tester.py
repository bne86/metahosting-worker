from queue_manager import qm
from worker import ExampleWorkerThread
from facade_listener import facade_listener

qm.subscribe('info', facade_listener)

th1 = ExampleWorkerThread(qm)
th1.daemon = True
th1.start()

# qm.publish('service_a', 'Create new1')
# qm.publish('service_a', 'Create new2')
# qm.publish('service_b', 'Create new3')
