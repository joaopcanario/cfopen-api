from flask import Blueprint, jsonify, request
# from flask import current_app as app

# from bson.objectid import ObjectId

from leaderboard.database import connect
from bson.json_util import dumps

# from leaderboard.championship import CFGamesBoard

# from pymongo import UpdateOne

import collections
# import requests
# import ast


cfopen_bp = Blueprint("cfopen_bp", __name__)


# @cfopen_bp.route('/affiliates', methods=['GET'])
# def affiliates():
#     """
#     """
#     entity = request.args.get('entity')
#     entity_name = request.args.get('entity_name')

#     if not entity and not entity_name:
#         return jsonify(response="not given any query params"), 404

#     mongo = connect("MONGO_READONLY").affiliatedb
#     affiliates_list = mongo.find({entity: entity_name})

#     Affiliate = collections.namedtuple('Affiliate',
#                                        'affiliate_id name country '
#                                        'region city state')

#     response = [Affiliate(a["affiliate_id"], a["name"], a["country"],
#                           "Latin America", a["city"], a["state"])._asdict()
#                 for a in affiliates_list]

#     return jsonify(response=response), 200


# @cfopen_bp.route('/entities', methods=['GET', 'POST'])
# def entities():

#     if request.method == 'POST':

#         try:
#             cf_entities = request.args.getlist('entity')
#             board_name = request.args.get('board_name')
#             owner = request.args.get('owner')

#             entities = [ast.literal_eval(entity) for entity in cf_entities]
#             data = {'name': board_name,
#                     'owner': owner,
#                     'entities': entities}

#             entitydb = connect().entitydb

#             uuid = str(entitydb.insert_one(data).inserted_id)
#         except Exception as e:
#             return jsonify(response=str(e)), 500

#         return jsonify(response={'uuid': uuid, 'board_name': board_name}), 201

#     if request.method == 'GET':
#         uuid = request.args.get('uuid')
#         board_name = request.args.get('board_name')

#         Board = collections.namedtuple('Board', 'uuid name owner entitites')

#         entitydb = connect("MONGO_READONLY").entitydb
#         result = entitydb.find({"_id": ObjectId(uuid)})
#         response = [Board(str(r['_id']), r['name'], r['owner'],
#                           r['entities'])._asdict()
#                     for r in result]

#         return jsonify(response=response), 200


# @cfopen_bp.route('/list', methods=['GET'])
# def list():
#     """
#     """
#     Board = collections.namedtuple('Board', 'id name owner')
#     response = [Board(str(r['_id']), r['name'], r['owner'])._asdict()
#                 for r in mongo.entitydb.find()]

#     return jsonify(response=response), 200


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
