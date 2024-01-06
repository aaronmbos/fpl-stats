import base64
from logger import init_logger
from scraper import scrape
from flask import Flask, request

logger = init_logger(__name__)
app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    try:
        logger.info("Parsing message.")

        envelope = request.get_json()
        if not envelope:
            msg = "No Pub/Sub message received"
            logger.error(f"Data aggregation skipped. {msg}")
            return f"Bad Request: {msg}", 204

        if (
            not isinstance(envelope, dict)
            or "message" not in envelope
            or "data" not in envelope["message"]
            or not base64.b64decode(envelope["message"]["data"]).decode("utf-8").strip()
            == "scrape"
        ):
            msg = "Invalid Pub/Sub message format"
            logger.error(f"Data aggregation skipped. {msg}")
            return f"Bad Request: {msg}", 204

        logger.info("Starting data aggregation.")
        scrape()
        logger.info("Data aggregation completed.")
        return ("", 204)
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)
        return f"Server Error.", 204
