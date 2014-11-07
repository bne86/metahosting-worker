import pika
# get yourself a running rabbitmq server with:
# docker run -d -p 5672:5672 -p 15672:15672 dockerfile/rabbitmq


import logging
from workers.common.thread_management import run_in_background


class BlockingPikaManager(object):
    def __init__(self):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()

    def publish(self, routing_key, message):
        logging.debug('[PikaManager] dispatching %s: %s', routing_key,
                      message)
        self.channel.basic_publish(exchange='', routing_key=routing_key,
                                   body=message)

    def subscribe(self, routing_key, listener):
        #  durable=True?
        self.channel.queue_declare(queue=routing_key)
        def callback_wrapper(ch, method, properties, body):
            listener(body)
            # we can use explicit acks
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
            # or use no_ack=True in basic_consume

        self.channel.basic_consume(callback_wrapper, queue=routing_key)
        #channel.start_consuming()

    def unsubscribe(self, routing_key, listener):
        logging.debug('Method not supported')

    def start(self):
        @run_in_background
        def subss():
            self.channel.start_consuming()

        subss()