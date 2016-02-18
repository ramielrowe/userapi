import json
import os
import unittest
import uuid

import requests

API_URL = os.environ.get('API_URL')


def create_test_user():
    return {
        'userid': str(uuid.uuid4()),
        'first_name': str(uuid.uuid4()),
        'last_name': str(uuid.uuid4())
    }


class FunctionalTestCases(unittest.TestCase):
    def _get(self, path):
        response = requests.get(API_URL + path)
        return response, response.json()

    def _post(self, path, data):
        response = requests.post(API_URL + path,
                                 data=json.dumps(data),
                                 headers={'Content-Type': 'application/json'})
        return response, response.json()

    def _put(self, path, data):
        response = requests.put(API_URL + path,
                                data=json.dumps(data),
                                headers={'Content-Type': 'application/json'})
        return response, response.json()

    def test_create_user(self):
        test_user = create_test_user()

        result, body = self._post('/users', test_user)

        self.assertEqual(201, result.status_code)
        self.assertEqual(test_user['userid'], body['userid'])
        self.assertEqual(test_user['last_name'], body['last_name'])
        self.assertEqual(test_user['first_name'], body['first_name'])

    def test_create_user_already_exists(self):
        test_user = create_test_user()

        result1, _ = self._post('/users', test_user)
        result2, _ = self._post('/users', test_user)

        self.assertEqual(201, result1.status_code)
        self.assertEqual(409, result2.status_code)

    def test_create_user_missing_field(self):
        test_user = create_test_user()
        del test_user['userid']

        result, _ = self._post('/users', test_user)

        self.assertEqual(400, result.status_code)

    def test_get_user(self):
        test_user = create_test_user()

        self._post('/users', test_user)
        result, user = self._get('/users/%s' % test_user['userid'])

        self.assertEqual(200, result.status_code)
        self.assertEqual(test_user['userid'], user['userid'])
        self.assertEqual(test_user['last_name'], user['last_name'])
        self.assertEqual(test_user['first_name'], user['first_name'])

    def test_get_user_does_not_exist(self):
        result, user = self._get('/users/userthatdoestexist')

        self.assertEqual(404, result.status_code)

    def test_update_user(self):
        test_user = create_test_user()

        result1, _ = self._post('/users', test_user)
        self.assertEqual(201, result1.status_code)

        test_user['first_name'] = 'andrew'
        result2, body = self._put('/users/%s' % test_user['userid'], test_user)
        self.assertEqual(200, result2.status_code)
        self.assertEqual('andrew', body['first_name'])

    def test_update_user_not_found(self):
        result, body = self._put('/users/userthatdoestexist',
                                 create_test_user())
        self.assertEqual(404, result.status_code)

    def test_update_user_change_userid(self):
        test_user = create_test_user()

        create_result, _ = self._post('/users', test_user)
        self.assertEqual(201, create_result.status_code)

        old_id = test_user['userid']
        test_user['userid'] = str(uuid.uuid4())
        update_result, body = self._put('/users/%s' % old_id, test_user)
        self.assertEqual(200, update_result.status_code)
        self.assertEqual(test_user['userid'], body['userid'])

        get_new_result, _ = self._get('/users/%s' % test_user['userid'])
        self.assertEqual(200, get_new_result.status_code)

        get_old_result, _ = self._get('/users/%s' % old_id)
        self.assertEqual(404, get_old_result.status_code)

    def test_update_user_change_userid_already_exists(self):
        test_user1 = create_test_user()
        test_user2 = create_test_user()

        create_result1, _ = self._post('/users', test_user1)
        create_result2, _ = self._post('/users', test_user2)
        self.assertEqual(201, create_result1.status_code)
        self.assertEqual(201, create_result2.status_code)

        old_id = test_user1['userid']
        test_user1['userid'] = test_user2['userid']
        update_result, body = self._put('/users/%s' % old_id, test_user1)
        self.assertEqual(409, update_result.status_code)
