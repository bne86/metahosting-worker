import ConfigParser
import logging
import os

_VARIABLES_FILE = 'envvars.ini'
_CONFIG_FILE = 'config.ini'


def get_configuration(section_name, config_file=None,
                      variables_file=_VARIABLES_FILE):
    if not config_file:
        config_file = _CONFIG_FILE
    var_config = ConfigParser.SafeConfigParser()
    var_config.read(variables_file)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    try:
        config_items = config.items(section=section_name)
    except ConfigParser.Error as err:
        logging.debug('Error while reading config: %s', err)
        return None
    try:
        env_overrides = var_config.options(section=section_name)
    except ConfigParser.NoSectionError:
        logging.debug('var config file %s not found', variables_file)
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
                return None
    return properties
