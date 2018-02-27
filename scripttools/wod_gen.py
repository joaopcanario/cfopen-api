from decouple import config
from pymongo import MongoClient

import collections


Wod = collections.namedtuple('Wod', 'year_id type max_reps time_cap')


if __name__ == '__main__':
    client = MongoClient(config('MONGO_URI'))
    mongo = client[config('MONGO_DBNAME')]

    data = [
        Wod('2017_1', 'fortime', '225', '20:00')._asdict(),
        Wod('2017_2', 'amrap', '0', '12:00')._asdict(),
        Wod('2017_3', 'fortime', '216', '24:00')._asdict(),
        Wod('2017_4', 'amrap', '0', '13:00')._asdict(),
        Wod('2017_5', 'fortime', '440', '40:00')._asdict(),
    ]

    affiliates = mongo.woddb
    affiliates.insert_many(data, bypass_document_validation=True)
