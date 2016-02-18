import functools
import json
import logging

import flask
from flask import g
from flask import jsonify
from flask import request

from userapi import exceptions
from userapi.db import api as db_api

APP = flask.Flask(__name__)

REQUIRED_USER_FIELDS = ['userid', 'first_name', 'last_name']
REQUIRED_GROUP_FIELDS = ['name']


@APP.before_first_request
def _setup():
    APP.logger.addHandler(logging.StreamHandler())
    APP.logger.setLevel(logging.INFO)


@APP.before_request
def _before_request():
    g.database = db_api.get_database()
    g.database.connect()


@APP.after_request
def _after_request(response):
    g.database.close()
    return response


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except exceptions.BaseAPIException as ae:
            response = jsonify({'exception': ae.__class__.__name__,
                                'code': ae.status_code})
            response.status_code = ae.status_code
            return response
        except:
            logging.exception('Internal server error')
            response = jsonify({'exception': 'InternalServerException',
                                'code': 500})
            response.status_code = 500
            return response

    return wrapper


def make_response(data, code=200):
    response = flask.make_response(json.dumps(data))
    response.status_code = code
    return response


def _check_fields(body, fields):
    for field in fields:
        if field not in body or not body[field]:
            raise exceptions.MissingRequiredFieldException()


@APP.route("/users/<userid>", methods=['GET'])
@handle_exceptions
def get_user(userid):
    return jsonify(db_api.get_user(userid).to_dict())


@APP.route("/users", methods=['POST'])
@handle_exceptions
def create_user():
    body = request.get_json()
    _check_fields(body, REQUIRED_USER_FIELDS)
    new_user = db_api.create_user(body)
    return make_response(new_user.to_dict(), code=201)


@APP.route("/users/<userid>", methods=['DELETE'])
@handle_exceptions
def delete_user(userid):
    db_api.delete_user(userid)
    return jsonify({})


@APP.route("/users/<userid>", methods=['PUT'])
@handle_exceptions
def update_user(userid):
    body = request.get_json()
    _check_fields(body, REQUIRED_USER_FIELDS)
    updated_user = db_api.update_user(userid, body)
    return jsonify(updated_user.to_dict())


@APP.route("/groups/<name>", methods=['GET'])
@handle_exceptions
def get_group(name):
    return make_response(db_api.get_group(name).to_list())


@APP.route("/groups", methods=['POST'])
@handle_exceptions
def create_group():
    body = request.get_json()
    _check_fields(body, REQUIRED_GROUP_FIELDS)
    new_group = db_api.create_group(body['name'])
    return make_response(new_group.to_dict(), code=201)


@APP.route("/groups/<name>", methods=['DELETE'])
@handle_exceptions
def delete_group(name):
    return jsonify({})


@APP.route("/groups/<name>", methods=['PUT'])
@handle_exceptions
def update_group(name):
    return jsonify({})
