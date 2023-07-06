import asyncio
from scraper import scrape


async def main():
    await scrape()


asyncio.run(main())
