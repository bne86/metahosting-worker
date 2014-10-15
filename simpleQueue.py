from collections import deque


class QueueManager(object):
    queues = dict()

    def publish(self, routing_key, message):
        if routing_key not in queues:
            print 'Error no queue for given routing key!'
            return
        listner = queues[routing_key].popleft()
        listner(message)
        queues[routing_key].append(listner)

    def subscribe(self, routing_key, listner):
        if routing_key not in queues:
            queues[routing_key] = deque()

        queues[routing_key].append(listner)

    def unsubscribe(self, routing_key, listner):
        if routing_key not in queues:
            print 'Error no queue for given routing key!'
            return
        q = queues.pop(routing_key)
        q.remove(listner)
        if len(q) > 0:
            queues[routing_key] = q
