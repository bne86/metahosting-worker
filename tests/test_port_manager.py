from unittest import TestCase
from workers.manager.port import PortManager


class TestPortManager(TestCase):
    def setUp(self):
        config = {'ports': '1:5'}
        self.port_manager = PortManager(config)

    def tearDown(self):
        self.port_manager = None

    def test_lacking_config(self):
        self.port_manager = PortManager({'foo': 'bar'})
        ports = self.port_manager.acquire_ports(1)
        self.assertIsNone(ports)

    def test_wrong_config_1(self):
        self.port_manager = PortManager({'ports': 'bar'})
        ports = self.port_manager.acquire_ports(1)
        self.assertIsNone(ports)

    def test_wrong_config_2(self):
        self.port_manager = PortManager({'ports': '1:asd'})
        ports = self.port_manager.acquire_ports(1)
        self.assertIsNone(ports)

    def test_wrong_config_3(self):
        self.port_manager = PortManager({'ports': '3:1'})
        ports = self.port_manager.acquire_ports(1)
        self.assertIsNone(ports)

    def test_acquire_ports(self):
        ports = self.port_manager.acquire_ports(2)
        self.assertIsNotNone(ports)

    def test_acquire_no_ports(self):
        ports = self.port_manager.acquire_ports(0)
        self.assertIsNotNone(ports)

    def test_acquire_to_many_ports(self):
        ports = self.port_manager.acquire_ports(6)
        self.assertIsNone(ports)

    def test_enough_ports_left(self):
        self.assertTrue(self.port_manager.enough_ports_left(5))

    def test_enough_ports_left_not(self):
        self.assertFalse(self.port_manager.enough_ports_left(6))

    def test_release_ports(self):
        acquired_ports = self.port_manager.acquire_ports(2)
        self.assertIsNotNone(acquired_ports)
        self.port_manager.release_ports(acquired_ports)

    def test_release_ports_empty(self):
        acquired_ports = self.port_manager.acquire_ports(0)
        self.assertIsNotNone(acquired_ports)
        self.port_manager.release_ports(acquired_ports)

    def test_update_used_ports(self):
        self.assertTrue(len(self.port_manager.used_ports) == 0)
        self.port_manager.acquire_ports(2)
        self.assertTrue(len(self.port_manager.used_ports) == 2)
        self.port_manager.update_used_ports([])
        self.assertTrue(len(self.port_manager.used_ports) == 2)
        self.port_manager.update_used_ports([6, 7])
        self.assertTrue(len(self.port_manager.used_ports) == 4)