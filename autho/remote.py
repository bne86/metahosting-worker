import requests


class RemoteAuthorizer(object):
    def __init__(self, url, user, password):
        self._url = url
        self._auth = (user, password)

    def is_user_instance(self, instance_id, user_id):
        res = requests.get('%s/%s/resources/%s' % (self._url, user_id,
                                                   instance_id))
        return res.status_code == 200

    def get_user_instances(self, user_id):
        res = requests.get('%s/%s/resources/' % (self._url, user_id))
        if res.status_code == 200:
            return res.json()['resources']
        return set()

    def make_owner(self, user_id, instance_id):
        # make owner:
        res = requests.put('%s/%s/resources/%s' % (self._url, user_id,
                                                   instance_id),
                           auth=self._auth)
        return res.status_code == 201

    def revoke_ownership(self, user_id, instance_id):
        # revoke ownership
        res = requests.delete('%s/%s/resources/%s' % (self._url, user_id,
                                                      instance_id),
                              auth=self._auth)
        return res.status_code == 204
