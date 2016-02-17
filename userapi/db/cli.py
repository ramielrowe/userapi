import argparse
import contextlib

from userapi.db import api as db_api


@contextlib.contextmanager
def connect_database():
    database = db_api.get_database()
    database.connect()
    try:
        yield database
    finally:
        database.close()


def create_tables():
    with connect_database() as database:
        db_api._create_tables(database)


def main():
    parser = argparse.ArgumentParser("UserAPI Database Utility")
    subparsers = parser.add_subparsers(help='sub-command help')

    create_tables_parser = subparsers.add_parser('create-tables')
    create_tables_parser.set_defaults(func=create_tables)

    args = parser.parse_args()
    args.func(args)