from autho import get_authorizer
from facade import Facade

authorizer = get_authorizer()
from stores import instance_store
from stores import type_store

facade = Facade(authorization=authorizer,
                type_store=type_store,
                instance_store=instance_store)
