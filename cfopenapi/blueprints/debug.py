from flask import Blueprint, jsonify

from ..database import connect

import cfopenapi


debug_bp = Blueprint("debug_bp", __name__)


@debug_bp.route('/ping')
def ping():
    '''
    Ping
    Checks API connectivity.

    __Response Model__

    <span style="margin-left:2em">Connectivity message</span>

    ---
    tags:
      - Debug
    responses:
      200:
        description: Ok
        type: string
    '''
    return jsonify("Pong!"), 200


@debug_bp.route('/version')
def version():
    '''
    Microservice Version
    Shows microservice current version.

    __Response Model__

    <span style="margin-left:2em">Microservice version</span>

    ---
    tags:
      - Debug
    responses:
      200:
        description: Ok
    '''
    return jsonify(f"API version: {cfopenapi.version}"), 200


@debug_bp.route('/refreshed')
def refreshed():
    '''
    Microservice Version
    Shows Ranking Database last update.

    __Response Model__

    <span style="margin-left:2em">Last update</span>

    ---
    tags:
      - Debug
    responses:
      200:
        description: Ok
    '''
    mongo = connect("MONGO_READONLY")
    result = mongo.rankingdb.find_one({"uuid": 'db_last_update'})

    last_update = str(result['updated_on'])
    return jsonify(f"Ranking DB last update was: {last_update}"), 200
