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
