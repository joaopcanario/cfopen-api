from flask import current_app as app

import celery


@celery.task()
def refresh_boards():
    from ..database import connect
    from ..championship.board import CFGamesBoard

    from pymongo import UpdateOne
    from decouple import config, Csv
    from bson.objectid import ObjectId
    from datetime import datetime

    with app.app_context():
        available_boards = app.config.get('OPEN_BOARDS')

    filter = {"name": { "$in": available_boards }}
    open_boards = connect("MONGO_READONLY").entitydb.find(filter)

    uuids = [result["_id"] for result in open_boards]

    ranks_uuids = []

    for uuid in uuids:
        filter = {"_id": ObjectId(uuid)}

        result = connect("MONGO_READONLY").entitydb.find_one(filter)

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            ranks_uuids.append(ranking.uuid)

            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        connect().rankingdb.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        connect().rankingdb.update_one({'uuid': 'db_last_update'},
                                       {"$set": {'updated_on': last_update}},
                                       upsert=True)

    return f'Success rankings uuids: {ranks_uuids}'
