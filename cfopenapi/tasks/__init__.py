from flask import current_app as app

import celery


@celery.task()
def refresh_boards():
    from ..database import connect
    from ..championship.board import CFGamesBoard

    from pymongo import UpdateOne
    from bson.objectid import ObjectId
    from datetime import datetime

    with app.app_context():
        available_boards = app.config.get('OPEN_BOARDS')

    entity_db = connect("MONGO_READONLY").entitydb
    ranking_db = connect().rankingdb

    open_boards = entity_db.find({"name": {"$in": available_boards}})

    uuids = [result["_id"] for result in open_boards]

    ranks_uuids = []

    for uuid in uuids:
        result = entity_db.find_one({"_id": ObjectId(uuid)})

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            ranks_uuids.append(ranking.uuid)

            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        ranking_db.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        ranking_db.update_one({'uuid': 'db_last_update'},
                              {"$set": {'updated_on': last_update}},
                              upsert=True)

    return f'Success rankings uuids: {ranks_uuids}'


@celery.task()
def refresh_cfbaboards():
    from ..database import connect
    from ..championship.board import Board, Athlete

    from pymongo import UpdateOne
    from bson.objectid import ObjectId
    from datetime import datetime

    athletescfba_db = connect("MONGO_READONLY").athletescfbadb
    rankingcfba_db = connect().rankingcfbadb

    uuids = ["dj8bd2j7et4fjxa01f"]

    uuids = [result["_id"] for result in open_boards]

    ranks_uuids = []

    for uuid in uuids:
        result = athletescfba_db.find({})
        athletes = Athlete.from_list(result, ordinal=5)

        board = Board(athletes, num_of_ordinals=5)
        board.generate_ranks(uuid)

        operations = []

        for ranking in board.ranks:
            ranks_uuids.append(ranking.uuid)

            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        rankingcfba_db.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        rankingcfba_db.update_one({'uuid': 'db_last_update'},
                                  {"$set": {'updated_on': last_update}},
                                  upsert=True)

    return f'Success rankings uuids: {ranks_uuids}'

