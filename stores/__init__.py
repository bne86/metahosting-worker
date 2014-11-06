import ConfigParser
import importlib

# TODO: decide whether this is a appropriate way to dynamically switch between
# different queue backends
# TODO:  still have to inject the config file path or using command line
settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))
imports = settings.get('persistency', 'backend').rsplit('.', 1)

store_module = importlib.import_module(imports[0])
store_class = getattr(store_module, imports[1])

instance_type_store = store_class()
instance_store = store_class()
