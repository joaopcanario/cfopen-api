from decouple import config
from pymongo import MongoClient

import collections


Wod = collections.namedtuple('Wod', 'year_id max_reps')


if __name__ == '__main__':
    client = MongoClient(config('MONGO_URI'))
    mongo = client[config('MONGO_DBNAME')]

    data = [
        Wod('2018_1', '0')._asdict(),
        Wod('2018_2', '0')._asdict(),
        Wod('2018_3', '0')._asdict(),
        Wod('2018_4', '0')._asdict(),
        Wod('2018_5', '0')._asdict(),
    ]

    affiliates = mongo.woddb
    affiliates.insert_many(data, bypass_document_validation=True)
