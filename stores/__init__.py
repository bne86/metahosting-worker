import ConfigParser
import importlib

#TODO: decide whether this is a appropriate way to dynamically switch between different queue backends
#TODO:  still have to inject the config file path or using command line
settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))
store = importlib.import_module(settings.get('persistency', 'backend'))

instance_type_store = store.Store()
instance_store = store.Store()