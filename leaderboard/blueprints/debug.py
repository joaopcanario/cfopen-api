from flask import Blueprint, jsonify

import leaderboard


debug_bp = Blueprint("debug_bp", __name__)


@debug_bp.route('/ping')
def ping():
    """
    file: docs/dbg_ping.yml
    """
    return jsonify(response="Pong!"), 200


@debug_bp.route('/version')
def version():
    """
    file: docs/dbg_version.yml
    """
    return jsonify(response=f"App version: {leaderboard.version}"), 200
