
class LocalAuthorizer(object):
    def __init__(self):
        self._ownership = dict()
        print('This authorizer must not be used in production')

    def is_user_instance(self, instance_id, user_id):
        return \
            user_id in self._ownership \
            and instance_id in self._ownership[user_id]

    def get_user_instances(self, user_id):
        if user_id not in self._ownership:
            return set()
        return self._ownership[user_id].copy()

    def make_owner(self, user_id, instance_id):
        if user_id not in self._ownership:
            self._ownership[user_id] = set()

        self._ownership[user_id].add(instance_id)
        return True

    def revoke_ownership(self, user_id, instance_id):
        if user_id not in self._ownership \
                or instance_id not in self._ownership[user_id]:
            return False
        self._ownership[user_id].remove(instance_id)

    def drop_all(self):
        self._ownership = dict()
