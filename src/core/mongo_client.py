import os
from dotenv import load_dotenv
from pymongo import MongoClient
from contextlib import contextmanager


@contextmanager
def CustomMongoClient():
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    yield mongo_client
    mongo_client.close()


if __name__ == "__main__":
    load_dotenv()
    with CustomMongoClient() as client:
        print(f"✅ Connection successful to: {client.address}")
        db = client.get_database("the_news_hub")
        collection_names = db.list_collection_names()
        for name in collection_names:
            print(f"  - {name}")
