import base64
from logger import init_logger
from scraper import scrape
from flask import Flask, request

logger = init_logger(__name__)
app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    try:
        logger.info("Starting data aggregation.")
        scrape()
        logger.info("Data aggregation completed.")
        return ("", 204)
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)
        return f"Server Error.", 204
