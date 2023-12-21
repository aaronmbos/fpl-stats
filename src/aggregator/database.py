from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

client = MongoClient(os.getenv("CONNECTION_STRING"), server_api=ServerApi("1"))
db = client.get_database("fpl-stats")


tmp_collection = f"{os.getenv('MONGO_COLLECTION')}_tmp"
bak_collection = f"{os.getenv('MONGO_COLLECTION')}_bak"
collection = os.getenv("MONGO_COLLECTION")


def init_db():
    # Drop temp collection if it doesn't exist
    db[tmp_collection].drop()
    # Drop the existing back up
    db[bak_collection].drop()
    # Back up the existing collection as it will be overwritten
    db[os.getenv("MONGO_COLLECTION")].aggregate(
        [{"$match": {}}, {"$out": bak_collection}]
    )


def insert_players(documents):
    result = db[tmp_collection].insert_many(documents)
    print(result.inserted_ids)


def swap_collections():
    db[tmp_collection].rename(collection, dropTarget=True)
