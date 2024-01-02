from dotenv import load_dotenv
import os
from logger import init_logger
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

logger = init_logger(__name__)

load_dotenv()

client = MongoClient(os.getenv("CONNECTION_STRING"), server_api=ServerApi("1"))
db = client.get_database("fpl-stats")


tmp_collection = f"{os.getenv('MONGO_COLLECTION')}_tmp"
bak_collection = f"{os.getenv('MONGO_COLLECTION')}_bak"
collection = os.getenv("MONGO_COLLECTION")


def init_db():
    # Drop temp collection if it exists
    logger.info("Dropping existing temp collection")
    db[tmp_collection].drop()
    # Drop the existing back up
    logger.info("Dropping existing back up collection")
    db[bak_collection].drop()
    # Back up the existing collection as it will be overwritten
    logger.info("Backing up the existing collection")
    db[os.getenv("MONGO_COLLECTION")].aggregate(
        [{"$match": {}}, {"$out": bak_collection}]
    )


def insert_players(documents):
    db[tmp_collection].insert_many(documents)


def swap_collections():
    logger.info("Swapping collections")
    db[tmp_collection].rename(collection, dropTarget=True)
