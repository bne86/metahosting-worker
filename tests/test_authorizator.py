import unittest
from autho import RemoteAuthorizer
from httmock import HTTMock, urlmatch
import logging

logging.basicConfig(format='[%(filename)s] %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)


class AuthorizatorTest(unittest.TestCase):
    def setUp(self):
        self.base_url = 'localhost:661'
        self.authorizer = RemoteAuthorizer('http://' + self.base_url,
                                           'user',
                                           'honda')

    def tearDown(self):
        pass

    def test_is_user_instance(self):
        with HTTMock(self.get_mock_for('/%s/resources/%s' % (1, 1), 200)):
            r = self.authorizer.is_user_instance(user_id=1, instance_id=1)
        self.assertTrue(r)

        with HTTMock(self.get_mock_for('/%s/resources/%s' % (2, 1), 404)):
            r = self.authorizer.is_user_instance(user_id=2, instance_id=1)
        self.assertFalse(r)

        with HTTMock(self.get_mock_for('/%s/resources/%s' % (1, 211), 404)):
            r = self.authorizer.is_user_instance(user_id=1, instance_id=211)
        self.assertFalse(r)

    def test_get_user_instances(self):
        # no instances:
        with HTTMock(self.get_mock_for('/1/resources/', 404)):
            r = self.authorizer.get_user_instances(user_id=1)
            self.assertIsNotNone(r)
            self.assertSetEqual(set(), r)

        content = {'user_id': 'aa', 'resources': ['1']}
        with HTTMock(self.get_responsive_mock_for('/1/resources/', 200, content
        )):
            r = self.authorizer.get_user_instances(user_id=1)

        self.assertIsNotNone(r)
        instance_id = '1'
        self.assertTrue(instance_id in r)

        content = {'user_id': 'aa', 'resources': []}
        with HTTMock(self.get_responsive_mock_for('/2/resources/', 200,
                                                  content)):
            r = self.authorizer.get_user_instances(user_id=2)
        self.assertIsNotNone(r)

    def test_make_owner(self):
        with HTTMock(self.get_mock_for('/%s/resources/%s' % (1, 1), 201)):
            r = self.authorizer.make_owner(user_id=1, instance_id=1)
        self.assertTrue(r)

    def test_revoke_ownership(self):
        with HTTMock(self.get_mock_for('/%s/resources/%s' % (1, 1), 204)):
            r = self.authorizer.revoke_ownership(user_id=1, instance_id=1)
        self.assertTrue(r)

        with HTTMock(self.get_mock_for('/%s/resources/%s' % (2, 2), 404)):
            r = self.authorizer.revoke_ownership(user_id=2, instance_id=2)
        self.assertFalse(r)

    def get_mock_for(self, path, code):
        @urlmatch(netloc='localhost:661', path=path)
        def my_mock(url, request):
            return {'status_code': code,
                    'content': ''}

        return my_mock

    def get_responsive_mock_for(self, path, code, content):
        @urlmatch(netloc='localhost:661', path=path)
        def my_mock(url, request):
            return {'content-type': 'application/json',
                    'status_code': code,
                    'content': content}

        return my_mock