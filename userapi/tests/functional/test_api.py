import json
import os
import unittest
import uuid

import requests

API_URL = os.environ.get('API_URL')


def create_test_user(groups=None):
    return {
        'userid': unicode(str(uuid.uuid4())),
        'first_name': unicode(str(uuid.uuid4())),
        'last_name': unicode(str(uuid.uuid4())),
        'groups': groups if groups else list()
    }


def create_test_group():
    return {
        'name': unicode(str(uuid.uuid4()))
    }


class FunctionalTestCases(unittest.TestCase):
    def _get(self, path):
        response = requests.get(API_URL + path)
        return response, response.json()

    def _delete(self, path):
        response = requests.delete(API_URL + path)
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

    def test_delete_user(self):
        test_user = create_test_user()

        create_result, _ = self._post('/users', test_user)
        self.assertEqual(201, create_result.status_code)

        get_before_result, _ = self._get('/users/%s' % test_user['userid'])
        self.assertEqual(200, get_before_result.status_code)

        delete_result, _ = self._delete('/users/%s' % test_user['userid'])
        self.assertEqual(200, delete_result.status_code)

        get_after_result, _ = self._get('/users/%s' % test_user['userid'])
        self.assertEqual(404, get_after_result.status_code)

    def test_create_group(self):
        test_group = create_test_group()

        create_result, body = self._post('/groups', test_group)

        self.assertEqual(201, create_result.status_code)
        self.assertEqual(test_group['name'], body['name'])

    def test_create_group_already_exists(self):
        test_group = create_test_group()

        create_result1, _ = self._post('/groups', test_group)
        create_result2, _ = self._post('/groups', test_group)

        self.assertEqual(201, create_result1.status_code)
        self.assertEqual(409, create_result2.status_code)

    def test_get_group(self):
        test_group = create_test_group()

        create_result, _ = self._post('/groups', test_group)
        get_result, body = self._get('/groups/%s' % test_group['name'])

        self.assertEqual(201, create_result.status_code)
        self.assertEqual(200, get_result.status_code)
        self.assertEqual([], body)

    def test_update_group(self):
        test_user = create_test_user()
        test_group = create_test_group()
        group_url = '/groups/%s' % test_group['name']

        create_user_result, _ = self._post('/users', test_user)
        self.assertEqual(201, create_user_result.status_code)

        create_group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, create_group_result.status_code)

        get_result1, get_group1 = self._get(group_url)
        self.assertEqual(200, get_result1.status_code)
        self.assertEqual([], get_group1)

        update_result, group_update = self._put(group_url,
                                                [test_user['userid']])
        self.assertEqual(200, update_result.status_code)
        self.assertEqual([test_user['userid']], group_update)

        get_result2, get_group2 = self._get(group_url)
        self.assertEqual(200, get_result2.status_code)
        self.assertEqual([test_user['userid']], get_group2)

    def test_update_group_does_not_exist(self):
        update_result, _ = self._put('/groups/groupthatdoestexist',[])
        self.assertEqual(404, update_result.status_code)

    def test_update_group_removes_user(self):
        test_user1 = create_test_user()
        test_user2 = create_test_user()
        test_group = create_test_group()
        group_url = '/groups/%s' % test_group['name']

        create_user_result1, _ = self._post('/users', test_user1)
        self.assertEqual(201, create_user_result1.status_code)
        create_user_result2, _ = self._post('/users', test_user2)
        self.assertEqual(201, create_user_result2.status_code)

        create_group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, create_group_result.status_code)

        update_result1, group_update1 = self._put(group_url,
                                                [test_user1['userid'],
                                                 test_user2['userid']])
        self.assertEqual(200, update_result1.status_code)
        self.assertEqual(sorted([test_user1['userid'],
                                 test_user2['userid']]),
                         sorted(group_update1))

        get_result1, get_group1 = self._get(group_url)
        self.assertEqual(200, get_result1.status_code)
        self.assertEqual(sorted([test_user1['userid'],
                                 test_user2['userid']]),
                         sorted(get_group1))

        update_result2, group_update2 = self._put(group_url,
                                                  [test_user1['userid']])
        self.assertEqual(200, update_result2.status_code)
        self.assertEqual([test_user1['userid']], group_update2)

        get_result2, get_group2 = self._get(group_url)
        self.assertEqual(200, get_result2.status_code)
        self.assertEqual([test_user1['userid']], get_group2)

    def test_delete_group(self):
        test_group = create_test_group()
        group_url = '/groups/%s' % test_group['name']

        create_group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, create_group_result.status_code)

        get_result1, get_group1 = self._get(group_url)
        self.assertEqual(200, get_result1.status_code)
        self.assertEqual([], get_group1)

        delete_group_result, _ = self._delete(group_url)
        self.assertEqual(200, delete_group_result.status_code)

        get_result2, _ = self._get(group_url)
        self.assertEqual(404, get_result2.status_code)

    def test_delete_group_does_not_exist(self):
        delete_group_result, _ = self._delete('/groups/groupthatdoestexist')
        self.assertEqual(404, delete_group_result.status_code)

    def test_create_user_with_group(self):
        test_group = create_test_group()
        test_user = create_test_user(groups=[test_group['name']])

        group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, group_result.status_code)

        user_result, user_body = self._post('/users', test_user)
        self.assertEqual(201, user_result.status_code)
        self.assertEqual(test_user['userid'], user_body['userid'])
        self.assertEqual(test_user['last_name'], user_body['last_name'])
        self.assertEqual(test_user['first_name'], user_body['first_name'])
        self.assertEqual(test_user['groups'], user_body['groups'])

        get_result, get_body = self._get('/users/%s' % test_user['userid'])
        self.assertEqual(200, get_result.status_code)
        self.assertEqual(test_user['userid'], get_body['userid'])
        self.assertEqual(test_user['last_name'], get_body['last_name'])
        self.assertEqual(test_user['first_name'], get_body['first_name'])
        self.assertEqual(test_user['groups'], get_body['groups'])

    def test_delete_group_removes_user_from_group(self):
        test_group = create_test_group()
        test_user = create_test_user(groups=[test_group['name']])

        group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, group_result.status_code)

        user_result, user_body = self._post('/users', test_user)
        self.assertEqual(201, user_result.status_code)
        self.assertEqual(test_user['userid'], user_body['userid'])
        self.assertEqual(test_user['last_name'], user_body['last_name'])
        self.assertEqual(test_user['first_name'], user_body['first_name'])
        self.assertEqual(test_user['groups'], user_body['groups'])

        delete_result, _ = self._delete('/groups/%s' % test_group['name'])
        self.assertEqual(200, delete_result.status_code)

        get_result, get_body = self._get('/users/%s' % test_user['userid'])
        self.assertEqual(200, get_result.status_code)
        self.assertEqual(test_user['userid'], get_body['userid'])
        self.assertEqual(test_user['last_name'], get_body['last_name'])
        self.assertEqual(test_user['first_name'], get_body['first_name'])
        self.assertEqual([], get_body['groups'])

    def test_delete_user_removes_user_from_group(self):
        test_group = create_test_group()
        test_user = create_test_user(groups=[test_group['name']])

        group_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, group_result.status_code)

        user_result, user_body = self._post('/users', test_user)
        self.assertEqual(201, user_result.status_code)
        self.assertEqual(test_user['userid'], user_body['userid'])
        self.assertEqual(test_user['last_name'], user_body['last_name'])
        self.assertEqual(test_user['first_name'], user_body['first_name'])
        self.assertEqual(test_user['groups'], user_body['groups'])

        delete_result, _ = self._delete('/users/%s' % test_user['userid'])
        self.assertEqual(200, delete_result.status_code)

        get_result, get_body = self._get('/groups/%s' % test_group['name'])
        self.assertEqual(200, get_result.status_code)
        self.assertEqual([], get_body)

    def test_update_user_with_group_add_user_to_group(self):
        test_user = create_test_user()
        user_url = '/users/%s' % test_user['userid']
        test_group = create_test_group()
        group_url = '/groups/%s' % test_group['name']

        user_create_result, _ = self._post('/users', test_user)
        self.assertEqual(201, user_create_result.status_code)

        group_create_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, group_create_result.status_code)

        test_user['groups'] = [test_group['name']]
        update_result, update_body = self._put(user_url, test_user)
        self.assertEqual(200, update_result.status_code)
        self.assertEqual(test_user['groups'], update_body['groups'])

        group_result, group_body = self._get(group_url)
        self.assertEqual(200, group_result.status_code)
        self.assertEqual([test_user['userid']], group_body)

    def test_update_user_without_group_removes_user_to_group(self):
        test_group = create_test_group()
        group_url = '/groups/%s' % test_group['name']
        test_user = create_test_user(groups=[test_group['name']])
        user_url = '/users/%s' % test_user['userid']

        group_create_result, _ = self._post('/groups', test_group)
        self.assertEqual(201, group_create_result.status_code)

        user_create_result, _ = self._post('/users', test_user)
        self.assertEqual(201, user_create_result.status_code)

        test_user['groups'] = []
        update_result, update_body = self._put(user_url, test_user)
        self.assertEqual(200, update_result.status_code)
        self.assertEqual([], update_body['groups'])

        group_result, group_body = self._get(group_url)
        self.assertEqual(200, group_result.status_code)
        self.assertEqual([], group_body)
