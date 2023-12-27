import asyncio
from scraper import scrape
import logging.config
from env_util import get_env
import newrelic


async def main():
    if get_env() != "prod":
        logger.info("Using dev logging configuration")
        logging.config.fileConfig("./logging_config/dev.ini")

    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting data aggregation.")
        await scrape()
        logger.info("Data aggregation completed.")
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)


asyncio.run(main())
