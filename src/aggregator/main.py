import base64
from quart import Quart, request
from logger import init_logger
from scraper import scrape

logger = init_logger(__name__)
app = Quart(__name__)


@app.route("/", methods=["POST"])
async def index():
    try:
        logger.info("Parsing message.")

        envelope = await request.get_json()
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
        await scrape()
        logger.info("Data aggregation completed.")
        return ("", 204)
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)
        return f"Server Error.", 204
