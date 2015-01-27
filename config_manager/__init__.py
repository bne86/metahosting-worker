import ConfigParser
import logging
import os

_VARIABLE_NAMES = 'envvars.ini'
_CONFIG_FILE = 'config.ini'


def get_configuration(section_name, config_file=_CONFIG_FILE,
                      variables=_VARIABLE_NAMES):
    var_config = ConfigParser.SafeConfigParser()
    var_config.read(variables)
    try:
        items = var_config.items(section=section_name)
    except ConfigParser.NoSectionError:
        logging.debug('var config file %s not found', variables)
        return None

    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    properties = {}
    for name, variable in items:
        if variable in os.environ:
            properties[name] = os.getenv(variable)
        else:
            try:
                properties[name] = config.get(section_name, name.lower())
            except:
                logging.error('Unable to initialize %s for %s', name,
                              section_name)
                return None
    return properties
