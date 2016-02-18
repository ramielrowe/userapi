import copy
import unittest

import mock

from userapi.db import api
from userapi import exceptions
from userapi.tests.unit import fixtures


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

        user = fixtures.TEST_USER
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
                          fixtures.TEST_USER)

    def test_get_user(self):
        mock_user = mock.MagicMock()
        self.User.get.return_value = mock_user

        new_user = api.get_user('test_id')

        self.assertEqual(new_user, mock_user)
        self.User.get.assert_called_once_with(self.User.userid == 'test_id')

    def test_get_user_does_not_exist(self):
        class TestException(Exception):
            pass
        self.User.DoesNotExist = TestException
        self.User.get.side_effect = self.User.DoesNotExist()

        self.assertRaises(exceptions.UserNotFoundException,
                          api.get_user,
                          'test_id')

        self.User.get.assert_called_once_with(self.User.userid == 'test_id')

    def test_update_user(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = True
        mock_user = mock.MagicMock()
        self.User.get.return_value = mock_user

        update_user = copy.deepcopy(fixtures.TEST_USER)
        update_user['first_name'] = 'kyle'
        new_user = api.update_user(update_user['userid'], update_user)

        self.assertEqual(new_user, mock_user)
        self.User.update.assert_called_once_with(**update_user)
        self.User.update.return_value.where.assert_called_once_with(
            self.User.userid == update_user['userid'])
        self.assertTrue(self.User.update.return_value
                                 .where.return_value
                                 .execute.called)
        self.User.get.assert_called_once_with(
            self.User.userid == update_user['userid'])

    def test_update_user_change_userid(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.side_effect) = [True, False]
        mock_user = mock.MagicMock()
        self.User.get.return_value = mock_user

        update_user = copy.deepcopy(fixtures.TEST_USER)
        old_id = update_user['userid']
        update_user['userid'] = 'new_id'
        new_user = api.update_user(old_id, update_user)

        self.assertEqual(new_user, mock_user)
        self.User.update.assert_called_once_with(**update_user)
        self.User.update.return_value.where.assert_called_once_with(
            self.User.userid == old_id)
        self.User.get.assert_called_once_with(
            self.User.userid == update_user['userid'])

    def test_update_user_change_userid_already_exists(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.side_effect) = [True, True]

        update_user = copy.deepcopy(fixtures.TEST_USER)
        old_id = update_user['userid']
        update_user['userid'] = 'new_id'

        self.assertRaises(exceptions.UserAlreadyExistsException,
                          api.update_user, old_id, update_user)

    def test_update_user_does_not_exist(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = False

        self.assertRaises(exceptions.UserNotFoundException,
                          api.update_user, 'some_id', fixtures.TEST_USER)

    def test_delete_user(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = True

        api.delete_user('some_id')

        self.User.delete.return_value.where.assert_called_once_with(
            self.User.userid == 'some_id'
        )

    def test_delete_user_does_not_exist(self):
        (self.User.select.return_value
                  .where.return_value
                  .exists.return_value) = False

        self.assertRaises(exceptions.UserNotFoundException,
                          api.delete_user, 'some_id')

    def test_create_group(self):
        mock_group = mock.MagicMock()

        (self.Group.select.return_value
                   .where.return_value
                   .exists.return_value) = False
        self.Group.return_value = mock_group

        group_name = 'test_group'
        new_group = api.create_group(group_name)

        self.assertEqual(new_group, mock_group)
        self.Group.assert_called_once_with(name=group_name)
        mock_group.save.assert_called_once_with()

    def test_create_group_already_exists(self):
        (self.Group.select.return_value
                   .where.return_value
                   .exists.return_value) = True

        group_name = 'test_group'
        self.assertRaises(exceptions.GroupAlreadyExistsException,
                          api.create_group, group_name)
        self.assertFalse(self.Group.called)
