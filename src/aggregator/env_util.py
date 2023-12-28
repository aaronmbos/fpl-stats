from dotenv import load_dotenv
import os


def get_env():
    load_dotenv()

    env = os.getenv("NEW_RELIC_ENVIRONMENT")

    if env == "production":
        return "production"
    else:
        return "development"
