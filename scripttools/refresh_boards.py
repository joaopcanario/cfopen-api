from leaderboard.championship import CFGamesBoard

from pymongo import MongoClient, UpdateOne

from decouple import config, Csv
from bson.objectid import ObjectId


def _connect(uri="MONGO_URI"):
    client = MongoClient(config(uri))
    mongo = client[config('MONGO_DBNAME')]

    return mongo


def refresh():
    available_boards = config('OPEN_BOARDS', default=[], cast=Csv())

    filter = {"name": { "$in": available_boards }}
    open_boards = _connect("MONGO_READONLY").entitydb.find(filter)

    uuids = [result["_id"] for result in open_boards]

    for uuid in uuids:
        filter = {"_id": ObjectId(uuid)}

        result = _connect("MONGO_READONLY").entitydb.find_one(filter)

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                           upsert=True)]

        _connect().rankingdb.bulk_write(operations)


if __name__ == '__main__':
    refresh()
