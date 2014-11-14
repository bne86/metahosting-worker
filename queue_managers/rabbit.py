import pika
# get yourself a running rabbitmq server with:
# docker run -d -p 5672:5672 -p 15672:15672 dockerfile/rabbitmq

# problems:
# 1, when start_consuming is called no new queues can be defined (so we need a
# predefined set of queues?)
# 2. if there is no callback registered start_consume exists instantly, so
#  we start it after the first subscription
# 3. how to stop the thread?
#  although it is not such a big problem with a daemon

import logging
import threading
import json

# TODO: configuration management:
# os.getenv('RABBIT_HOST', 'localhost')
# open question: here or in config?


class BlockingPikaManager():
    def __init__(self):
        logging.debug('Initializing...')
        credentials = pika.PlainCredentials('guest', 'guest')
        self.parameters = \
            pika.ConnectionParameters('localhost', 5672, '/', credentials)

        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.thread = threading.Thread(target=self.channel.start_consuming)
        self.thread.setDaemon(True)

    def reconnect(self):
        if self.channel.is_open:
            self.channel.close()

        if self.connection.is_open:
            self.connection.close()

        self.connection.connect()
        self.channel.open()

    def publish(self, routing_key, message):
        logging.debug('dispatching %s: %s', routing_key,
                      message)
        #self.channel.queue_declare(routing_key)
        self.channel.basic_publish(exchange='', routing_key=routing_key,
                                   body=json.dumps(message))

    def subscribe(self, routing_key, listener):
        #  durable=True?
        #        self.channel.queue_declare(queue=routing_key)
        def callback_wrapper(ch, method, properties, body):
            #TODO: type check from props
            listener(json.loads(body))
            # we can use explicit acks
            # or use no_ack=True in basic_consume
            ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.debug('Subscribe request for %s' % routing_key)
        self.channel.basic_consume(callback_wrapper, queue=routing_key)
        if not self.thread.is_alive():
            self.thread.start()

    def unsubscribe(self, routing_key, listener):
        logging.info('Method not supported')

