import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://fantasy.premierleague.com/statistics")

        page_count = await get_page_count(page)
        await get_player_data(page)
        # for x in range(1, page_count + 1):
        #     print(f"Page {x} of {page_count}")

        await browser.close()


async def get_player_data(page):
    data = await page.locator(
        "main > div > div:nth-child(2) > div > div > table"
    ).get_attribute("class")
    print(data)


async def get_page_count(page):
    text = await page.locator(
        "main > div > div:nth-child(2) > div > div > div > div"
    ).all_text_contents()
    return int(text[1].split(" ")[-1])


asyncio.run(main())
