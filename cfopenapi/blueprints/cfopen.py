from flask import Blueprint, jsonify, request

from ..database import connect
from ..championship.board import Athlete


cfopen_bp = Blueprint("cfopen_bp", __name__)


@cfopen_bp.route('/leaderboards', methods=['GET'])
def leaderboards():
    '''
    Brazil custom leaderboards
    Get state or region leaderboards filtered by divisions, male or female.

    __Available leaderboards__

    - Bahia

    __Available Divisions__

    - Masculino
    - Feminino
    - Boys (14-15)
    - Girls (14-15)
    - Boys (16-17)
    - Girls (16-17)
    - Men (18-34)
    - Women (18-34)
    - Men (35-39)
    - Women (35-39)
    - Men (40-44)
    - Women (40-44)
    - Men (45-49)
    - Women (45-49)
    - Men (50-54)
    - Women (50-54)
    - Men (55-59)
    - Women (55-59)
    - Men (60+)
    - Women (60+)

    ---
    tags:
      - Open
    summary: Get custom leaderboard
    parameters:
      - name: name
        in: query
        description: The board name.
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
    name = request.args.get('name')
    division = request.args.get('division')

    mongo = connect("MONGO_READONLY")

    if not name or not division:
        return jsonify(f'Missing required parameters: name={name}, '
                       f'division={division}'), 200

    result = mongo.entitydb.find_one({"name": name})

    filter_search = {"uuid": f"{result['_id']}_{division}"}
    result = mongo.rankingdb.find_one(filter_search)

    response = Athlete.from_list_to_leaderboard(result['athletes'])

    return jsonify(response), 200


@cfopen_bp.route('/cfba', methods=['GET'])
def cfba():
    '''
    CFBA Barra custom leaderboards
    Get CFBA Barra leaderboard filtered by genders, male (M) or female (F).

    __Available leaderboards__

    - CFBA Barra

    ---
    tags:
      - Open
    summary: Get custom leaderboard
    parameters:
      - name: gender
        in: query
        description: Athletes gender.
        type: string
        required: true
    responses:
      200:
        description: Ranking of athletes by gender
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
    gender = request.args.get('gender')

    mongo = connect("MONGO_READONLY")

    if not gender:
        return jsonify(f'Missing required parameters: gender={gender}'), 200
    elif gender not in ['M', 'F']:
        return jsonify('Gender must be M or F'), 200

    division = "Masculino" if gender == "M" else "Feminino"

    filter_search = {"uuid": f"dj8bd2j7et4fjxa01f_{division}"}
    result = mongo.rankingcfbadb.find_one(filter_search)

    response = Athlete.from_list_to_leaderboard(result['athletes'])

    return jsonify(response), 200
