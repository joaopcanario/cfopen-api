from flask import Blueprint, jsonify

import leaderboard


debug_bp = Blueprint("debug_bp", __name__)


@debug_bp.route('/ping')
def ping():
    '''
    Ping
    Checks API connectivity.

    __Response Model__

    <span style="margin-left:2em">__response__: Connectivity message</span>

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

    <span style="margin-left:2em">__response__: Microservice version</span>

    ---
    tags:
      - Debug
    responses:
      200:
        description: Ok
    '''
    return jsonify(f"API version: {leaderboard.version}"), 200
