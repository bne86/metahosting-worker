def get_facade():
    from autho import get_authorizer
    from facade import Facade
    from stores import get_stores
    from queue_managers import send_message

    type_store, instance_store = get_stores()
    authorizer = get_authorizer()

    return Facade(authorization=authorizer,
                  type_store=type_store,
                  instance_store=instance_store,
                  send_method=send_message)
