import logging

import flask

APP = flask.Flask(__name__)

@APP.before_first_request
def _setup():
    APP.logger.addHandler(logging.StreamHandler())
    APP.logger.setLevel(logging.INFO)


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
