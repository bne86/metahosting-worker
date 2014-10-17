from Queue import Queue
import threading
import time

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'This is a service_a for doing lot of cool stuff'


class ExampleWorkerThread(threading.Thread):
    def __init__(self, queue_manger):
        super(ExampleWorkerThread, self).__init__()
        self.subject = instance_class['name']
        self.queue_manger = queue_manger
        self.queue = Queue()
        queue_manger.subscribe(self.subject, self.listener)
        queue_manger.publish('info', {'msg': 'instance_type',
                                      'class': instance_class})

    def log(self, entry):
        print('[%sWorker-%s] %s\n' % (self.subject, self.getName(), entry))

    def listener(self, message):
        # this could be a separate method and queue (outside of the thread)
        self.queue.put(message)

    def do_work(self, msg):
        self.log('Creating %s instance (id=%s)' % (self.subject,
                                                   msg['id']))
        time.sleep(5)
        msg['status'] = 'running'
        self.queue_manger.publish('info',
                                  {'msg': 'instace_info', 'instance': msg})

    def run(self):
        while True:
            msg = self.queue.get()
            self.do_work(msg)
            self.queue.task_done()
