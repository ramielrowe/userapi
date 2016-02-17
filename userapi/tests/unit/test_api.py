import json
import unittest

from userapi import api


TEST_USER = {
    'first_name': 'Joe',
    'last_name': 'Smith',
    'userid': 'jsmith',
    'groups': ['admins', 'users']
}

TEST_GROUP = {'name': 'users'}


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = api.APP.test_client()

    def _req(self, func, url, data):
        return func(url,
                    data=json.dumps(data),
                    headers={'content-type': 'application/json'})

    def _post(self, url, data):
        return self._req(self.app.post, url, data)

    def _put(self, url, data):
        return self._req(self.app.put, url, data)

    def test_get_user(self):
        self.app.get('/users/a')

    def test_create_user(self):
        self._post('/users', TEST_USER)

    def test_delete_user(self):
        self.app.delete('/users/a')

    def test_update_user(self):
        self._put('/users', TEST_USER)

    def test_get_group(self):
        self.app.get('/groups/a')

    def test_create_group(self):
        self._post('/groups', TEST_GROUP)

    def test_delete_group(self):
        self.app.delete('/groups/a')

    def test_update_group(self):
        self._put('/groups', TEST_GROUP)
