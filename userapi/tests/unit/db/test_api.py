import unittest

import mock

from userapi.db import api
from userapi import exceptions


class APITestCase(unittest.TestCase):
    def setUp(self):
        user_patcher = mock.patch.object(api, 'User')
        self.User = user_patcher.start()
        self.addCleanup(user_patcher.stop)

        group_patcher = mock.patch.object(api, 'Group')
        self.Group = group_patcher.start()
        self.addCleanup(group_patcher.stop)

        usergroups_patcher = mock.patch.object(api, 'UserGroups')
        self.UserGroups = usergroups_patcher.start()
        self.addCleanup(usergroups_patcher.stop)

    def test_create_user(self):
        mock_user = mock.MagicMock()

        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = False
        self.User.return_value = mock_user

        user = {'userid': 'amelton',
                'first_name': 'andrew',
                'last_name': 'melton'}
        new_user = api.create_user(user)

        self.assertEqual(new_user, mock_user)
        self.User.assert_called_once_with(userid=user['userid'],
                                          first_name=user['first_name'],
                                          last_name=user['last_name'])
        mock_user.save.assert_called_once_with()

    def test_create_user_already_exists(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = True

        self.assertRaises(exceptions.UserAlreadyExistsException,
                          api.create_user,
                          {'userid': 'amelton',
                           'first_name': 'andrew',
                           'last_name': 'melton'})
