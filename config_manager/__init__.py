import ConfigParser
import logging
import os

_VARIABLE_NAMES = 'envvars.ini'
_CONFIG_FILE = 'config.ini'


def get_configuration(section_name, config_file=None,
                      variables=_VARIABLE_NAMES):
    if not config_file:
        config_file = _CONFIG_FILE
    var_config = ConfigParser.SafeConfigParser()
    var_config.read(variables)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)

    config_items = config.items(section=section_name)
    try:
        env_overrides = var_config.options(section=section_name)
    except ConfigParser.NoSectionError:
        logging.debug('var config file %s not found', variables)
        env_overrides = []

    properties = {}
    for name, variable in config_items:
        if name in env_overrides:
            tmp = var_config.get(section=section_name, option=name)
            if tmp in os.environ:
                properties[name] = os.getenv(tmp)
        else:
            try:
                properties[name] = variable
            except ConfigParser.NoOptionError:
                logging.error('Unable to initialize %s for %s', name,
                              section_name)
                return None
    print properties
    return properties
