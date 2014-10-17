from collections import deque


class QueueManager(object):
    queues = dict()

    def publish(self, routing_key, message):
        print('[QueueManager] dispatching %s: %s' % (routing_key, message))
        if not self.queue_exist(routing_key):
            print('Error no queue for given routing key %s!' % routing_key)
            return
        listener = self.queues[routing_key].popleft()
        listener(message)
        self.queues[routing_key].append(listener)

    def subscribe(self, routing_key, listener):
        if not self.queue_exist(routing_key):
            self.queues[routing_key] = deque()

        self.queues[routing_key].append(listener)

    def unsubscribe(self, routing_key, listener):
        if not self.queue_exist(routing_key):
            print('Error no queue for given routing key %s!' % routing_key)
            return
        q = self.queues.pop(routing_key)
        q.remove(listener)
        if len(q) > 0:
            self.queues[routing_key] = q

    def queue_exist(self, routing_key):
        if routing_key not in self.queues:
            return False
        return True
