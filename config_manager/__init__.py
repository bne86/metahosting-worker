import ConfigParser
import logging
import os

_VARIABLES_FILE = 'envvars.ini'
_CONFIG_FILE = 'config.ini'


def get_configuration(section_name, config_file=None,
                      variables_file=None):
    if not config_file:
        logging.debug('Using %s for configuration', _CONFIG_FILE)
        config_file = _CONFIG_FILE
    if not variables_file:
        logging.debug('Using %s for env configuration', _VARIABLES_FILE)
        variables_file = _VARIABLES_FILE
    try:
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        config_items = config.items(section=section_name)
    except ConfigParser.Error as err:
        logging.error(err)
        return None
    try:
        var_config = ConfigParser.SafeConfigParser()
        var_config.read(variables_file)
        env_overrides = var_config.options(section=section_name)
    except ConfigParser.Error as err:
        logging.debug(err)
        env_overrides = []

    properties = {}
    for name, variable in config_items:
        overwritten = False
        if name in env_overrides:
            tmp = var_config.get(section=section_name, option=name)
            if tmp in os.environ:
                overwritten = True
                properties[name] = os.getenv(tmp)
        if not overwritten:
            try:
                properties[name] = variable
            except ConfigParser.NoOptionError:
                logging.error('Unable to initialize %s for %s', name,
                              section_name)
    logging.debug('{}, {}'.format(section_name, str(properties)))
    return properties


def get_instance_configuration(section_name, config_file=None,
                               variables_file=None):
    properties = get_configuration(section_name=section_name,
                                   config_file=config_file,
                                   variables_file=variables_file)
    for item in os.environ:
        if 'INSTANCE_ENVIRONMENT' in item:
            properties[item.split('__')[1]] = os.getenv(item)
    return properties


def get_backend_class(config):
    """
    :param config: configuration containing a 'backend' item
    :return: backend class
    """
    import importlib
    class_data = config['backend'].split(".")
    module_path = ".".join(class_data[:-1])
    module = importlib.import_module(module_path)
    class_str = class_data[-1]
    return getattr(module, class_str)