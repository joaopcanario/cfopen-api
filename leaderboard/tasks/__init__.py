from leaderboard.database import connect
from leaderboard.championship import CFGamesBoard

from pymongo import UpdateOne
from decouple import config, Csv
from bson.objectid import ObjectId

import celery


@celery.task()
def refresh_boards():
    available_boards = config('OPEN_BOARDS', default=[], cast=Csv())

    filter = {"name": { "$in": available_boards }}
    open_boards = connect("MONGO_READONLY").entitydb.find(filter)

    uuids = [result["_id"] for result in open_boards]

    for uuid in uuids:
        filter = {"_id": ObjectId(uuid)}

        result = connect("MONGO_READONLY").entitydb.find_one(filter)

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                           upsert=True)]

        connect().rankingdb.bulk_write(operations)
