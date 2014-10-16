import threading
from Queue import Queue


class ExampleWorkerThread(threading.Thread):
    
    def __init__(self, queue_manger, subject='example'):
        super(ExampleWorkerThread, self).__init__()
        self.subject = subject
        self.queue_manger = queue_manger
        self.queue = Queue()
        queue_manger.subscribe(subject, self.listener)
        queue_manger.publish('info', subject)

    def listener(self, message):
        print 'Working thread ', self.subject, 'recieved message: ', message
        self.queue.put(message)

    def run(self):
        while True:
            msg = self.queue.get()
            print 'Working on ', msg, ' for ', self.subject
            time.wait(5)
            self.queue.task_done()
