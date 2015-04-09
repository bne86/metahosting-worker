from queue_managers.rabbit import BlockingPikaManager
from queue_managers import send_message, subscribe, get_message_subject
import config_manager
import unittest
import os


def callback(msg):
    print 'Incoming message %s' % msg


class RabbitTest(unittest.TestCase):
    def setUp(self):
        config_manager._CONFIG_FILE = os.getenv('TEST_CONFIG', 'config.ini')
        config = config_manager.get_configuration(section_name='messaging')
        self.queue_name = 'testing_queue'
        self.manager = BlockingPikaManager(host=config['host'], port=int(config[
            'port']), user='guest', password='guest', queue=self.queue_name)

    def tearDown(self):
        pass

    def test_publish(self):
        self.manager.publish(routing_key=self.queue_name,
                             message={'foo': 'bar'})

    def test_subscribe(self):
        self.manager.subscribe(routing_key=self.queue_name,
                               listener=callback)
        self.manager.publish(routing_key=self.queue_name, message={
            'foo': 'bar'})

    def test_unsubsribe(self):
        with self.assertRaises(NotImplementedError):
            self.manager.unsubscribe(routing_key=self.queue_name,
                                     listener=lambda x: None)

    def test_send_message(self):
        send_message(routing_key=self.queue_name,
                     subject='nothing',
                     message={'foo': 'bar'})

    def test_alt_subscribe(self):
        subscribe(routing_key=self.queue_name,
                  callback=callback)
        send_message(routing_key=self.queue_name,
                     subject='nothing',
                     message={'foo': 'bar'})

    def test_get_subject(self):
        msg = {'content': 'content', 'foo': 'bar'}
        self.assertIsNone(get_message_subject(msg))
        subject = 'Grass is green'
        msg['subject'] = subject
        self.assertTrue('subject' in msg)
        res = get_message_subject(msg)
        self.assertEquals(res, subject)
        self.assertFalse('subject' in msg)
