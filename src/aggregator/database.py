from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

client = MongoClient(os.getenv("CONNECTION_STRING"), server_api=ServerApi("1"))
db = client.get_database("fpl-stats")


def insert_players(documents):
    tmp_collection = f"{os.getenv('MONGO_COLLECTION')}_tmp"
    result = db[tmp_collection].insert_many(documents)
    print(result.inserted_ids)


def swap_collections():
    original_collection = os.getenv("MONGO_COLLECTION")
    tmp_collection = f"{original_collection}_tmp"
    db[tmp_collection].rename(original_collection, dropTarget=True)
