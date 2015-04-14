import ConfigParser
import os
import unittest
from mock import Mock
from config_manager import get_configuration, get_backend_class
from tempfile import NamedTemporaryFile


class Backend():
    pass


class ConfigManagerTest(unittest.TestCase):
    def setUp(self):
        cfg = ConfigParser.ConfigParser()
        cfg.add_section('some_section')
        cfg.set('some_section', 'host', 'foo')
        cfg.set('some_section', 'port', '29192')
        cfg.set('some_section', 'backend', 'tests.test_config_manager.Backend')
        self.config_file = NamedTemporaryFile(mode='w', delete=False)
        cfg.write(self.config_file)
        self.config_file.close()

        self.env_file = NamedTemporaryFile(mode='w', delete=False)
        cfg = ConfigParser.ConfigParser()
        cfg.add_section('some_section')
        cfg.set('some_section', 'host', 'SOME_HOST_NAME')
        cfg.set('some_section', 'port', 'SOME_PORT_NAME')

        cfg.add_section('other_section')
        cfg.set('other_section', 'foo', 'bar')
        cfg.write(self.env_file)
        self.env_file.close()

    def tearDown(self):
        self.config_file.unlink(self.config_file.name)
        self.env_file.unlink(self.env_file.name)

    def test_not_existing_section(self):
        configuration = get_configuration('not-existing-section',
                                          config_file=self.config_file.name)
        self.assertIsNone(configuration)

    def test_existing_config(self):
        configuration = get_configuration(section_name='some_section',
                                          config_file=self.config_file.name,
                                          variables_file=self.env_file.name)
        self.assertTrue('host' in configuration)
        self.assertTrue('port' in configuration)
        self.assertEquals(configuration['host'], 'foo')
        self.assertEquals(configuration['port'], '29192')
        self.assertFalse('foo' in configuration)

    def test_existing_env(self):
        os.environ['SOME_HOST_NAME'] = 'bar'
        os.environ['SOME_PORT_NAME'] = '6661'
        configuration = get_configuration(section_name='some_section',
                                          config_file=self.config_file.name,
                                          variables_file=self.env_file.name)
        self.assertTrue('host' in configuration)
        self.assertTrue('port' in configuration)
        self.assertEquals(configuration['host'], 'bar')
        self.assertEquals(configuration['port'], '6661')
        self.assertFalse('foo' in configuration)
        os.environ.pop('SOME_HOST_NAME')
        os.environ.pop('SOME_PORT_NAME')

    def test_get_backend_class(self):
        configuration = get_configuration(section_name='some_section',
                                          config_file=self.config_file.name,
                                          variables_file=self.env_file.name)
        backend_class = get_backend_class(configuration)
        self.assertTrue('Backend' in str(backend_class))


