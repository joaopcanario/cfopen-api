def connect(uri="MONGO_URI"):
    from pymongo import MongoClient
    from decouple import config

    client = MongoClient(config(uri), retryWrites=False)
    mongo = client[config('MONGO_DBNAME')]

    return mongo
