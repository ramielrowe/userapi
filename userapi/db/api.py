import copy
import os

import peewee
from playhouse import postgres_ext

from userapi import exceptions

DATABASE = postgres_ext.PostgresqlExtDatabase(None, register_hstore=False)


class User(peewee.Model):
    class Meta:
        database = DATABASE

    userid = peewee.TextField(unique=True, index=True)
    first_name = peewee.TextField()
    last_name = peewee.TextField()

    def to_dict(self):
        return {'userid': self.userid,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'groups': [ug.group.name for ug in self.usergroups]}


class Group(peewee.Model):
    class Meta:
        database = DATABASE

    name = peewee.TextField(unique=True, index=True)

    def to_dict(self):
        return {'name': self.name}

    def to_list(self):
        return [ug.user.userid for ug in self.usergroups]


class UserGroups(peewee.Model):
    class Meta:
        database = DATABASE

    user = peewee.ForeignKeyField(User, index=True, related_name='usergroups')
    group = peewee.ForeignKeyField(Group, index=True, related_name='usergroups')


def get_database(database=None, user=None, password=None, host=None):
    database = database or os.environ.get('POSTGRES_DB', None)
    user = user or os.environ.get('POSTGRES_USER', None)
    password = password or os.environ.get('POSTGRES_PASSWORD', None)
    host = host or os.environ.get('POSTGRES_HOST', None)

    DATABASE.init(database, user=user, password=password, host=host)
    return DATABASE


def _create_tables(database):
    database.create_tables([User, Group, UserGroups], safe=True)


def get_user(userid):
    try:
        return User.get(User.userid == userid)
    except User.DoesNotExist as dne:
        raise exceptions.UserNotFoundException


def _user_exists(userid):
    return User.select().where(User.userid == userid).exists()


def _group_exists(name):
    return Group.select().where(Group.name == name).exists()


def create_user(user):
    userid = user['userid']

    if _user_exists(userid):
        raise exceptions.UserAlreadyExistsException()

    requested_groups = [get_group(name) for name in user.get('groups', list())]

    new_user = User(userid=userid,
                    first_name=user['first_name'],
                    last_name=user['last_name'])
    new_user.save()

    for group in requested_groups:
        UserGroups(user=new_user, group=group).save()

    return new_user


def _get_requested_groups(user):
    return {name: get_group(name) for name in user.get('groups', list())}


def _save_user_fields(db_user, api_user):
    db_user.userid = api_user['userid']
    db_user.first_name = api_user['first_name']
    db_user.last_name = api_user['last_name']
    db_user.save()


def _remove_unrequested_groups(user, requested_groups):
    existing_groups = set()
    for usergroup in user.usergroups:
        if usergroup.group.name not in requested_groups:
            usergroup.delete_instance()
        else:
            existing_groups.add(usergroup.group.name)
    return existing_groups


def _add_new_groups(user, requested_groups, existing_groups):
    for name, group in requested_groups.iteritems():
        if name not in existing_groups:
            UserGroups(user=user, group=group).save()


def update_user(userid, api_user):
    db_user = get_user(userid)

    if userid != api_user['userid'] and _user_exists(api_user['userid']):
        raise exceptions.UserAlreadyExistsException()

    requested_groups = _get_requested_groups(api_user)

    _save_user_fields(db_user, api_user)

    existing_groups = _remove_unrequested_groups(db_user, requested_groups)
    _add_new_groups(db_user, requested_groups, existing_groups)

    return get_user(api_user['userid'])


def delete_user(userid):
    user = get_user(userid)
    UserGroups.delete().where(UserGroups.user == user).execute()
    User.delete().where(User.userid == userid).execute()


def get_group(name):
    try:
        return Group.get(Group.name == name)
    except Group.DoesNotExist as dne:
        raise exceptions.UserNotFoundException


def create_group(name):
    if _group_exists(name):
        raise exceptions.GroupAlreadyExistsException()

    new_group = Group(name=name)
    new_group.save()
    return new_group


def _remove_unrequested_users(group, requested_users):
    existing_users = set()
    for usergroup in group.usergroups:
        if usergroup.user.userid not in requested_users:
            usergroup.delete_instance()
        else:
            existing_users.add(usergroup.user.userid)
    return existing_users


def _add_new_users(group, requested_users, existing_users):
    for userid, user in requested_users.iteritems():
        if userid not in existing_users:
            UserGroups(user=user, group=group).save()


def update_group(name, member_ids):
    group = get_group(name)
    requested_users = {userid: get_user(userid) for userid in member_ids}
    existing_users = _remove_unrequested_users(group, requested_users)
    _add_new_users(group, requested_users, existing_users)
    return get_group(name)


def delete_group(name):
    group = get_group(name)
    UserGroups.delete().where(UserGroups.group == group).execute()
    group.delete_instance()
