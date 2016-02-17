import logging

import flask
from flask import g

from userapi.db import api as db_api

APP = flask.Flask(__name__)


@APP.before_first_request
def _setup():
    APP.logger.addHandler(logging.StreamHandler())
    APP.logger.setLevel(logging.INFO)


@APP.before_request
def before_request():
    g.database = db_api.get_database()
    g.database.connect()


@APP.after_request
def after_request(response):
    g.database.close()
    return response


@APP.route("/users/<userid>", methods=['GET'])
def get_user(userid):
    return ''


@APP.route("/users", methods=['POST'])
def create_user():
    return ''


@APP.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid):
    return ''


@APP.route("/users/<userid>", methods=['PUT'])
def update_user(userid):
    return ''


@APP.route("/groups/<name>", methods=['GET'])
def get_group(name):
    return ''


@APP.route("/groups", methods=['POST'])
def create_group():
    return ''


@APP.route("/groups/<name>", methods=['DELETE'])
def delete_group(name):
    return ''


@APP.route("/groups/<name>", methods=['PUT'])
def update_group(name):
    return ''
