import os
from pymongo import MongoClient
from contextlib import contextmanager


@contextmanager
def CustomMongoClient():
    mongo_client = MongoClient(
        host="mongodb://localhost:27017/",
        port=27017,
        username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
        password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
        authSource="admin",
    )
    yield mongo_client
    mongo_client.close()
