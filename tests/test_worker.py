from workers import Worker, _get_uuid
import unittest


class WorkerTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_get_uuid(self):
        config = {'uuid_file': 'tests/files/uuid.txt'}
        uuid = _get_uuid(config)
        self.assertIs(str, type(uuid))

    def test_get_uuid_wrong_path(self):
        config = {'uuid_file': 'wrong/path'}
        uuid = _get_uuid(config)
        self.assertIs(str, type(uuid))

    def test_get_uuid_wrong_content(self):
        config = {'uuid_file': 'tests/files/uuid_wrong.txt'}
        uuid = _get_uuid(config)
        self.assertIs(str, type(uuid))
