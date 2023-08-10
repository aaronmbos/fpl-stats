from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

client = MongoClient(os.getenv("CONNECTION_STRING"), server_api=ServerApi("1"))
db = client.get_database("fpl-stats")


def insert_many(documents):
    result = db[os.getenv("MONGO_COLLECTION")].insert_many(documents)
    print(result.inserted_ids)
