from queue_manager.simple_queue import QueueManager

qm = QueueManager()


def send_message(routing_key, subject, message):
    msg = message.copy()
    msg['subject'] = subject
    qm.publish(routing_key, msg)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')