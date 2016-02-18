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

    def test_get_group(self):
        mock_group = mock.MagicMock()
        self.Group.get.return_value = mock_group

        group = api.get_group('test_name')

        self.assertEqual(mock_group, group)
        self.Group.get.assert_called_once_with(self.Group.name == 'test_name')

    def test_get_group_does_not_exist(self):
        class TestException(Exception):
            pass
        self.Group.DoesNotExist = TestException
        self.Group.get.side_effect = self.Group.DoesNotExist()

        self.assertRaises(exceptions.UserNotFoundException,
                          api.get_group,
                          'test_name')
        self.Group.get.assert_called_once_with(self.Group.name == 'test_name')

    def test_remove_unrequested_users_no_changes(self):
        mock_user = mock.MagicMock()
        mock_user.userid = 'id1'
        requested_users = {mock_user.userid: mock_user}

        mock_group = mock.MagicMock()
        mock_usergroup = mock.MagicMock()
        mock_usergroup.user = mock_user
        mock_usergroup.group = mock_group
        mock_group.usergroups = [mock_usergroup]

        existing_users = api._remove_unrequested_users(mock_group,
                                                       requested_users)

        self.assertEqual(1, len(existing_users))
        self.assertTrue(mock_user.userid in existing_users)

    def test_remove_unrequested_users_removes_user(self):
        mock_user1 = mock.MagicMock()
        mock_user1.userid = 'id1'
        mock_user2 = mock.MagicMock()
        mock_user2.userid = 'id2'
        requested_users = {mock_user1.userid: mock_user1}

        mock_group = mock.MagicMock()
        mock_usergroup1 = mock.MagicMock()
        mock_usergroup1.user = mock_user1
        mock_usergroup1.group = mock_group
        mock_usergroup2 = mock.MagicMock()
        mock_usergroup2.user = mock_user2
        mock_usergroup2.group = mock_group
        mock_group.usergroups = [mock_usergroup1, mock_usergroup2]

        existing_users = api._remove_unrequested_users(mock_group,
                                                       requested_users)

        self.assertEqual(1, len(existing_users))
        self.assertTrue(mock_user1.userid in existing_users)
        self.assertFalse(mock_user2.delete_instance.called)

    def test_remove_unrequested_users_removes_all_users(self):
        mock_user1 = mock.MagicMock()
        mock_user1.userid = 'id1'
        mock_user2 = mock.MagicMock()
        mock_user2.userid = 'id2'

        mock_group = mock.MagicMock()
        mock_usergroup1 = mock.MagicMock()
        mock_usergroup1.user = mock_user1
        mock_usergroup1.group = mock_group
        mock_usergroup2 = mock.MagicMock()
        mock_usergroup2.user = mock_user2
        mock_usergroup2.group = mock_group
        mock_group.usergroups = [mock_usergroup1, mock_usergroup2]

        existing_users = api._remove_unrequested_users(mock_group, {})

        self.assertEqual(0, len(existing_users))

    def test_add_new_users(self):
        mock_user1 = mock.MagicMock()
        mock_user1.userid = 'id1'
        mock_user2 = mock.MagicMock()
        mock_user2.userid = 'id2'
        requested_users = {mock_user1.userid: mock_user1,
                           mock_user2.userid: mock_user2}
        mock_group = mock.MagicMock()

        api._add_new_users(mock_group, requested_users, {mock_user1.userid})

        self.UserGroups.assert_called_once_with(user=mock_user2,
                                                group=mock_group)
        self.assertTrue(self.UserGroups.return_value.save.called)

    def test_add_new_users_no_new(self):
        mock_user = mock.MagicMock()
        mock_user.userid = 'id1'
        requested_users = {mock_user.userid: mock_user}
        mock_group = mock.MagicMock()

        api._add_new_users(mock_group, requested_users, {mock_user.userid})

        self.assertFalse(self.UserGroups.called)

    @mock.patch.object(api, '_add_new_users')
    @mock.patch.object(api, '_remove_unrequested_users')
    @mock.patch.object(api, 'get_user')
    @mock.patch.object(api, 'get_group')
    def test_update_group(self, mock_get_group, mock_get_user,
                          mock_remove_unrequested_users,
                          mock_add_new_users):
        mock_group = mock.MagicMock()
        mock_get_group.return_value = mock_group
        mock_user1 = mock.MagicMock()
        mock_user1.userid = 'id1'
        mock_user2 = mock.MagicMock()
        mock_user2.userid = 'id2'
        mock_get_user.side_effect = [mock_user1, mock_user2]
        requested_users = {mock_user1.userid: mock_user1,
                           mock_user2.userid: mock_user2}
        existing_users = {mock_user1.userid}
        mock_remove_unrequested_users.return_value = existing_users

        group = api.update_group('test_group', [mock_user1.userid,
                                                mock_user2.userid])

        self.assertEqual(mock_group, group)
        mock_get_group.assert_has_calls([mock.call('test_group'),
                                        mock.call('test_group')])
        mock_get_user.assert_has_calls([mock.call(mock_user1.userid),
                                        mock.call(mock_user2.userid)])
        mock_remove_unrequested_users.assert_called_once_with(
            mock_group, requested_users
        )
        mock_add_new_users.assert_called_once_with(mock_group,
                                                   requested_users,
                                                   existing_users)

    def test_delete_group(self):
        mock_group = mock.MagicMock()
        self.Group.get.return_value = mock_group

        api.delete_group('test_name')

        self.Group.get.assert_called_once_with(self.Group.name == 'test_name')
        self.assertTrue(mock_group.delete_instance.called)
        self.assertTrue(self.UserGroups.delete.called)
        self.UserGroups.delete.return_value.where.assert_called_once_with(
            self.UserGroups.group == mock_group
        )
        self.assertTrue(self.UserGroups.delete.return_value
                                       .where.return_value
                                       .execute.called)
