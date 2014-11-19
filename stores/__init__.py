from ConfigParser import ConfigParser
import importlib

def get_instance(settings, section_name):
    backend = settings.get(section_name, 'backend')
    module_name, class_name = backend.rsplit('.', 1)
    module = importlib.import_module(module_name)
    clazz = getattr(module, class_name)

    items = settings.items(section_name)
    items.remove(('backend', backend))

    instance = clazz(config={k: v for k, v in items})
    return instance


config = ConfigParser()
config.readfp(open('config.ini'))

type_store = get_instance(config, 'type_store')
instance_store = get_instance(config, 'instance_store')
