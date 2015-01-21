import pika
# get yourself a running rabbitmq server with:
# docker run -d -p 5672:5672 -p 15672:15672 dockerfile/rabbitmq

# problems:
# 1, when start_consuming is called no new queues can be defined (so we need a
# predefined set of queues?)
# 2. if there is no callback registered start_consume exists instantly, so
# we start it after the first subscription
# 3. how to stop the thread?
# although it is not such a big problem with a daemon

import logging
import threading
import json


class BlockingPikaManager(object):
    def __init__(self, host, port):
        logging.debug('Initializing...')
        credentials = pika.PlainCredentials('guest', 'guest')
        logging.warning('Using default credentials')
        self.parameters = \
            pika.ConnectionParameters(host=host, port=port,
                                      virtual_host='', credentials=credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        logging.debug('Connected to messaging')
        self.thread = threading.Thread(target=self.channel.start_consuming)
        self.thread.setDaemon(True)

    def publish(self, routing_key, message):
        logging.debug('dispatching %s: %s', routing_key, message)
        self.channel.basic_publish(exchange='', routing_key=routing_key,
                                   body=json.dumps(message),
                                   properties=pika.BasicProperties(
                                       content_type='application/json'))

    def subscribe(self, routing_key, listener):
        def callback_wrapper(channel, method, properties, body):
            if properties.content_type != 'application/json':
                logging.error('Invalid content_type: %s',
                              properties.content_type)
                channel.basic_reject(delivery_tag=method.delivery_tag,
                                     requeue=False)
                logging.debug('Discarding message: %r', body)
                return

            listener(json.loads(body))
            channel.basic_ack(delivery_tag=method.delivery_tag)

        logging.debug('Subscribe request for: %s', routing_key)
        self.channel.basic_consume(callback_wrapper, queue=routing_key)
        if not self.thread.is_alive():
            self.thread.start()

    def unsubscribe(self, routing_key, listener):
        # self.channel.basic_cancel(consumer_tag=listener.__name__)
        raise NotImplementedError
