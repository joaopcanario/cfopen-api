from flask import Blueprint, jsonify, request

from leaderboard.database import connect
from bson.json_util import dumps

import collections

cfopen_bp = Blueprint("cfopen_bp", __name__)


@cfopen_bp.route('/leaderboards', methods=['GET'])
def leaderboards():
    uuid = request.args.get('uuid')
    division = request.args.get('division')

    filter_search = {"uuid": f"{uuid}_{division}"}
    result = connect("MONGO_READONLY").rankingdb.find(filter_search)

    Leaderboard = collections.namedtuple('Leaderboard', 'id name ranking')
    response = [Leaderboard(str(r['uuid']), r['name'], r['athletes'])._asdict()
                for r in result]

    return jsonify(response=response), 200
