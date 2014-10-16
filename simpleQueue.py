from collections import deque


class QueueManager(object):
    queues = dict()

    def publish(self, routing_key, message):
        if routing_key not in self.queues:
            print 'Error no queue for given routing key!'
            return
        listner = self.queues[routing_key].popleft()
        listner(message)
        self.queues[routing_key].append(listner)

    def subscribe(self, routing_key, listner):
        if routing_key not in self.queues:
            self.queues[routing_key] = deque()

        self.queues[routing_key].append(listner)

    def unsubscribe(self, routing_key, listner):
        if routing_key not in self.queues:
            print 'Error no queue for given routing key!'
            return
        q = self.queues.pop(routing_key)
        q.remove(listner)
        if len(q) > 0:
            self.queues[routing_key] = q
