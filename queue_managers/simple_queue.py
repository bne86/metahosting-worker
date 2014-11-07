from collections import deque
import logging


class QueueManager(object):

    def __init__(self):
        self.queues = dict()

    def publish(self, routing_key, message):
        logging.debug('[QueueManager] dispatching %s: %s', routing_key,
                      message)
        if not self.queue_exist(routing_key):
            logging.error('Error no queue for given routing key "%s"',
                          routing_key)
            return None
        listener = self.queues[routing_key].popleft()
        listener(message)
        self.queues[routing_key].append(listener)

    def subscribe(self, routing_key, listener):
        if not self.queue_exist(routing_key):
            self.queues[routing_key] = deque()

        self.queues[routing_key].append(listener)

    def unsubscribe(self, routing_key, listener):
        if not self.queue_exist(routing_key):
            logging.error('Error no queue for given routing key "%s"',
                          routing_key)
            return
        queue = self.queues.pop(routing_key)
        queue.remove(listener)
        if len(queue) > 0:
            self.queues[routing_key] = queue

    def queue_exist(self, routing_key):
        if routing_key not in self.queues:
            return False
        return True
