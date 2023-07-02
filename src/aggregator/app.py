import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://fantasy.premierleague.com/statistics")

        await accept_cookies(page)

        page_count = await get_page_count(page)

        await get_player_data(page)
        # for x in range(1, page_count + 1):
        #     print(f"Page {x} of {page_count}")

        await browser.close()


async def accept_cookies(page):
    await page.locator("button#onetrust-accept-btn-handler").click()


async def get_player_data(page):
    player_info_btns = page.locator(
        "main > div > div:nth-child(2) > div > div > table tbody tr > td:nth-child(1) > button:nth-child(1)"
    )

    for i in range(0, await player_info_btns.count()):
        await player_info_btns.nth(i).click()
        print(
            (
                await page.locator(
                    'div#root-dialog > div[role="presentation"] > dialog > div > div:nth-child(2) > div:nth-child(1)'
                ).all_inner_texts()
            )[0].split("\n")
        )
        await page.locator(
            'div#root-dialog > div[role="presentation"] > dialog > div div:nth-child(1) button'
        ).click()


async def get_page_count(page):
    text = await page.locator(
        "main > div > div:nth-child(2) > div > div > div > div"
    ).all_text_contents()
    return int(text[1].split(" ")[-1])


asyncio.run(main())
