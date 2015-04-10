import logging


class PortManager():
    def __init__(self, worker_conf):
        self.port_range = set()
        if 'ports' in worker_conf and ':' in worker_conf['ports']:
            start, end = worker_conf['ports'].split(':')
            try:
                start = int(start)
                end = int(end)
                if start <= end:
                    for item in range(start, end+1):
                        self.port_range.add(item)
                else:
                    logging.error('start port must be smaller then end port')
            except ValueError as err:
                logging.error('Wrong port configuration given %s', err)
        self.port_range = frozenset(self.port_range)
        self.used_ports = set()

    def acquire_ports(self, count):
        available_ports = set(self.port_range.difference(self.used_ports))
        if count <= len(available_ports):
            acquired_ports = []
            for item in range(0, count):
                port = available_ports.pop()
                self.used_ports.add(port)
                acquired_ports.append(port)
            logging.debug("Acquired ports: %s", acquired_ports)
            return acquired_ports
        return None

    def enough_ports_left(self, count):
        if count > len(set(self.port_range.difference(self.used_ports))):
            return False
        else:
            return True

    def release_ports(self, ports):
        logging.debug('Releasing ports %s', str(ports))
        for port in ports:
            try:
                self.used_ports.remove(port)
            except KeyError as err:
                logging.debug('Port %s already released', port, err)

    def update_used_ports(self, ports):
        for port in ports:
            self.used_ports.add(port)
        logging.debug("Used ports: %s", self.used_ports)
