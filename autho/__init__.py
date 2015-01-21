import os
from autho.local import LocalAuthorizer
from autho.remote import RemoteAuthorizer

HOST = 'AUTHO_PORT_5000_TCP_ADDR'
PORT = 'AUTHO_PORT_5000_TCP_PORT'


def get_authorizer():
    if PORT in os.environ and HOST in os.environ:
        url = 'http://%s:%s' % (os.environ.get(HOST),
                                os.environ.get(PORT))
        return RemoteAuthorizer(url=url, user='service2', password='simple')
    print 'set environment variables:%s %s to use remote authorizer' % \
          (HOST, PORT)
    return LocalAuthorizer()
