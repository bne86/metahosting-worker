from facade import register_instance_type, update_instance


def facade_listener(message):
    if 'msg' not in message:
        print('Invalid message format')
        return

    msg_subject = message['msg']
    if msg_subject == 'instance_type':
        register_instance_type(message['class'])
    if msg_subject == 'instance_info':
        instance = message['instance']
        update_instance(instance['id'], instance)
