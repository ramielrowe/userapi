import copy
import json
import mock
import unittest

from userapi import api
from userapi import exceptions
from userapi.tests.unit import fixtures


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = api.APP.test_client()
        db_api_patcher = mock.patch.object(api, 'db_api')
        self.mock_db = db_api_patcher.start()
        self.addCleanup(db_api_patcher.stop)

    def _req(self, func, url, data=None):
        if data:
            response = func(url,
                            data=json.dumps(data),
                            headers={'content-type': 'application/json'})
        else:
            response = func(url)
        return response, json.loads(response.data)

    def _post(self, url, data):
        return self._req(self.app.post, url, data)

    def _put(self, url, data):
        return self._req(self.app.put, url, data)

    def _get(self, url):
        return self._req(self.app.get, url)

    def _delete(self, url):
        return self._req(self.app.delete, url)

    def test_get_user(self):
        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = fixtures.TEST_USER
        self.mock_db.get_user.return_value = mock_user

        resp, new_user = self._get('/users/test')

        self.assertEqual(new_user, fixtures.TEST_USER)
        self.mock_db.get_user.assert_called_once_with('test')

    def test_get_user_does_not_exist(self):
        exc = exceptions.UserNotFoundException()
        self.mock_db.get_user.side_effect = exc

        resp, _ = self._get('/users/test')

        self.assertEqual(exc.status_code, resp.status_code)
        self.mock_db.get_user.assert_called_once_with('test')

    def test_create_user(self):
        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = fixtures.TEST_USER
        self.mock_db.create_user.return_value = mock_user

        resp, new_user = self._post('/users', fixtures.TEST_USER)

        self.assertEqual(201, resp.status_code)
        self.assertEqual(new_user, fixtures.TEST_USER)
        self.mock_db.create_user.assert_called_once_with(fixtures.TEST_USER)

    def test_create_user_with_groups(self):
        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = fixtures.TEST_USER_WITH_GROUP
        self.mock_db.create_user.return_value = mock_user

        resp, new_user = self._post('/users', fixtures.TEST_USER_WITH_GROUP)

        self.assertEqual(201, resp.status_code)
        self.assertEqual(new_user, fixtures.TEST_USER_WITH_GROUP)
        self.mock_db.create_user.assert_called_once_with(
            fixtures.TEST_USER_WITH_GROUP)

    def test_create_user_with_groups_not_list(self):
        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = fixtures.TEST_USER_WITH_GROUP
        self.mock_db.create_user.return_value = mock_user

        request = copy.deepcopy(fixtures.TEST_USER_WITH_GROUP)
        request['groups'] = 'not a list'
        resp, _ = self._post('/users', request)

        self.assertEqual(400, resp.status_code)
        self.assertFalse(self.mock_db.create_user.called)

    def test_create_user_already_exists(self):
        exc = exceptions.UserAlreadyExistsException()
        self.mock_db.create_user.side_effect = exc

        resp, _ = self._post('/users', fixtures.TEST_USER)

        self.assertEqual(exc.status_code, resp.status_code)
        self.mock_db.create_user.assert_called_once_with(fixtures.TEST_USER)

    def test_create_user_missing_field(self):
        exc = exceptions.MissingRequiredFieldException()
        self.mock_db.create_user.side_effect = exc

        resp, _ = self._post('/users', {'first_name': 'andrew'})

        self.assertEqual(exc.status_code, resp.status_code)
        self.assertFalse(self.mock_db.create_user.called)

    def test_delete_user(self):
        resp, _ = self._delete('/users/test')
        self.assertEqual(200, resp.status_code)
        self.mock_db.delete_user.assert_called_once_with('test')

    def test_update_user(self):
        updated_user = copy.deepcopy(fixtures.TEST_USER)
        updated_user['first_name'] = 'kyle'

        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = updated_user
        self.mock_db.update_user.return_value = mock_user

        resp, body = self._put('/users/test', updated_user)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(updated_user, body)
        self.mock_db.update_user.assert_called_once_with('test',
                                                         updated_user)

    def test_update_user_with_groups(self):
        updated_user = copy.deepcopy(fixtures.TEST_USER_WITH_GROUP)
        updated_user['first_name'] = 'kyle'

        mock_user = mock.MagicMock()
        mock_user.to_dict.return_value = updated_user
        self.mock_db.update_user.return_value = mock_user

        resp, body = self._put('/users/test', updated_user)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(updated_user, body)
        self.mock_db.update_user.assert_called_once_with('test',
                                                         updated_user)

    def test_update_user_missing_field(self):
        updated_user = copy.deepcopy(fixtures.TEST_USER)
        del updated_user['first_name']

        resp, body = self._put('/users/test', updated_user)

        self.assertEqual(400, resp.status_code)
        self.assertFalse(self.mock_db.update_user.called)

    def test_update_user_groups_not_list(self):
        updated_user = copy.deepcopy(fixtures.TEST_USER)
        updated_user['groups'] = {}

        resp, body = self._put('/users/test', updated_user)

        self.assertEqual(400, resp.status_code)
        self.assertFalse(self.mock_db.update_user.called)

    def test_get_group(self):
        user_list = ['andrew', 'sam']
        mock_group = mock.MagicMock()
        mock_group.to_list.return_value = user_list
        self.mock_db.get_group.return_value = mock_group

        resp, body = self._get('/groups/admins')

        self.assertEqual(200, resp.status_code)
        self.assertEqual(body, user_list)

    def test_create_group(self):
        mock_group = mock.MagicMock()
        mock_group.to_dict.return_value = fixtures.TEST_GROUP
        self.mock_db.create_group.return_value = mock_group

        resp, body = self._post('/groups', fixtures.TEST_GROUP)

        self.assertEqual(201, resp.status_code)
        self.assertEqual(fixtures.TEST_GROUP['name'], body['name'])
        self.mock_db.create_group.assert_called_once_with(
            fixtures.TEST_GROUP['name'])

    def test_update_group(self):
        member_ids = ['user1', 'user2']
        mock_group = mock.MagicMock()
        mock_group.to_list.return_value = member_ids
        self.mock_db.update_group.return_value = mock_group

        resp, body = self._put('/groups/admins', member_ids)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(member_ids, body)
        self.mock_db.update_group.assert_called_once_with('admins', member_ids)

    def test_update_group_not_list(self):
        member_ids = {}

        resp, _ = self._put('/groups/admins', member_ids)

        self.assertEqual(400, resp.status_code)
        self.assertFalse(self.mock_db.update_group.called)

    def test_delete_group(self):
        resp, _ = self._delete('/groups/admins')
        self.assertEqual(200, resp.status_code)
        self.mock_db.delete_group.assert_called_once_with('admins')
