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
                'last_name': self.last_name}


class Group(peewee.Model):
    class Meta:
        database = DATABASE

    name = peewee.TextField(unique=True, index=True)


class UserGroups(peewee.Model):
    class Meta:
        database = DATABASE

    user = peewee.ForeignKeyField(User, index=True)
    group = peewee.ForeignKeyField(Group, index=True)


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


def create_user(user):
    userid = user['userid']

    if User.select().where(User.userid == userid).exists():
        raise exceptions.UserAlreadyExistsException()

    new_user = User(userid=userid,
                    first_name=user['first_name'],
                    last_name=user['last_name'])
    new_user.save()
    return new_user


def update_user(userid, user):
    pass


def delete_user(userid):
    pass


def get_group(name):
    pass


def create_group(name):
    pass


def update_group(name, members):
    pass


def delete_group(name):
    pass
