import json
import mock
import unittest

from userapi import api
from userapi import exceptions


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
        db_api_patcher = mock.patch.object(api, 'db_api')
        self.mock_db = db_api_patcher.start()
        self.addCleanup(db_api_patcher.stop)

    def _req(self, func, url, data):
        response = func(url,
                        data=json.dumps(data),
                        headers={'content-type': 'application/json'})
        return response, json.loads(response.data)

    def _post(self, url, data):
        return self._req(self.app.post, url, data)

    def _put(self, url, data):
        return self._req(self.app.put, url, data)

    def test_get_user(self):
        self.app.get('/users/a')

    def test_create_user(self):
        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = TEST_USER
        self.mock_db.create_user.return_value = mock_user

        resp, new_user = self._post('/users', TEST_USER)

        self.assertEqual(new_user, TEST_USER)
        self.mock_db.create_user.assert_called_once_with(TEST_USER)

    def test_create_user_already_exists(self):
        exc = exceptions.UserAlreadyExistsException()
        self.mock_db.create_user.side_effect = exc

        resp, _ = self._post('/users', TEST_USER)

        self.assertEqual(resp.status_code, exc.status_code)
        self.mock_db.create_user.assert_called_once_with(TEST_USER)

    def test_create_user_missing_field(self):
        exc = exceptions.MissingRequiredFieldException()
        self.mock_db.create_user.side_effect = exc

        resp, _ = self._post('/users', {'first_name': 'andrew'})

        self.assertEqual(resp.status_code, exc.status_code)
        self.assertFalse(self.mock_db.create_user.called)

    def test_delete_user(self):
        self.app.delete('/users/a')

    def test_update_user(self):
        self._put('/users/a', TEST_USER)

    def test_get_group(self):
        self.app.get('/groups/a')

    def test_create_group(self):
        self._post('/groups', TEST_GROUP)

    def test_delete_group(self):
        self.app.delete('/groups/a')

    def test_update_group(self):
        self._put('/groups/a', TEST_GROUP)
