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
    var_config = ConfigParser.SafeConfigParser()
    var_config.read(variables_file)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    try:
        config_items = config.items(section=section_name)
    except ConfigParser.Error as err:
        logging.error('Error while reading config: %s', err)
        return None
    try:
        env_overrides = var_config.options(section=section_name)
    except ConfigParser.Error as err:
        logging.error('Error while reading environment config: %s', err)
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
