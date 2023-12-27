from dotenv import load_dotenv
import os


def get_env():
    load_dotenv()

    env = os.getenv("ENV")

    if env == "prod":
        return "prod"
    else:
        return "dev"
