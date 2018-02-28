from flask import Blueprint, jsonify, request

from leaderboard.database import connect
from bson.json_util import dumps

import collections

cfopen_bp = Blueprint("cfopen_bp", __name__)


@cfopen_bp.route('/leaderboards', methods=['GET'])
def leaderboards():
    '''
    Brazil custom leaderboards
    Get state or region leaderboards filtered by divisions, male or female.

    ---
    tags:
      - Open
    summary: Get custom leaderboard
    parameters:
      - name: uuid
        in: query
        description: The board unique identifier.
        type: string
        required: true
      - name: division
        in: query
        description: Athletes division.
        type: string
        required: true
    responses:
      200:
        description: Ranking of athletes by division
        schema:
            type: object
            properties:
                ranking:
                    type: array
                    items:
                        schema:
                            properties:
                                affiliateName:
                                    type: string
                                competitorName:
                                    type: string
                                overallScore:
                                    type: string
                                profilePic:
                                    type: string
                                scores:
                                    type: array
                                    items:
                                        schema:
                                            properties:
                                                scoreDisplay:
                                                    type: string
                                                rank:
                                                    type: string
                                                score:
                                                    type: string
    '''
    uuid = request.args.get('uuid')
    division = request.args.get('division')

    if not uuid or not division:
        return jsonify(f'Missing required parameters: uuid={uuid}, '
                       f'division={division}'), 200

    filter_search = {"uuid": f"{uuid}_{division}"}
    result = connect("MONGO_READONLY").rankingdb.find(filter_search)

    response = []

    for r in result:
        for athlete in r['athletes']:
            scores = [{'rank': score['rank'],
                        'scoreDisplay': score['scoreDisplay'],
                        'score': score['score']
                      } for score in athlete['scores']]

            response.append({
                'affiliateName': athlete['affiliateName'],
                'competitorName': athlete['competitorName'],
                'overallScore': athlete['overallScore'],
                'profilePic': athlete['profilePic'],
                'scores': scores
            })

    return jsonify(response), 200
