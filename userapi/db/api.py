import os

import peewee
from playhouse import postgres_ext

DATABASE = postgres_ext.PostgresqlExtDatabase(None, register_hstore=False)


class User(peewee.Model):
    userid = peewee.TextField(unique=True, index=True)
    first_name = peewee.TextField()
    last_name = peewee.TextField()


class Group(peewee.Model):
    name = peewee.TextField(unique=True, index=True)


class UserGroups(peewee.Model):
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
    database.create_tables([User, Group, UserGroups])


def get_user(userid):
    pass


def create_user(userid, user):
    pass


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
