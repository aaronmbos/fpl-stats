import asyncio
from logger import init_logger
from scraper import scrape

logger = init_logger(__name__)


async def main():
    try:
        logger.info("Starting data aggregation.")
        await scrape()
        logger.info("Data aggregation completed.")
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)


asyncio.run(main())
