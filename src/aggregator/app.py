import asyncio
from scraper import scrape
import logging.config


async def main():
    logging.config.fileConfig("./logging_config/dev.ini")

    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting data aggregation.")
        await scrape()
        logger.info("Data aggregation completed.")
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)


asyncio.run(main())
