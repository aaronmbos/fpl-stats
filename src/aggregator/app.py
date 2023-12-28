import newrelic.agent

newrelic.agent.initialize()
import asyncio
from scraper import scrape
import logging.config
from env_util import get_env


async def main():
    newrelic.agent.register_application(timeout=10.0)
    if get_env() != "production":
        logging.config.fileConfig("./logging_config/dev.ini")
        logger.info("Using dev logging configuration")

    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting data aggregation.")
        await scrape()
        logger.info("Data aggregation completed.")
    except:
        logger.error("An error occurred during data aggregation.", exc_info=True)
    finally:
        newrelic.agent.shutdown_agent(timeout=10)


asyncio.run(main())
