from asyncio import sleep
from playwright.async_api import async_playwright


async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://fantasy.premierleague.com/statistics")

        await accept_cookies(page)

        page_count = await get_page_count(page)

        for page_idx in range(0, page_count):
            await get_player_data(page)
            if page_idx < page_count - 1:
                await click_next_page(page)

        await browser.close()


async def accept_cookies(page):
    await page.locator("button#onetrust-accept-btn-handler").click()


async def get_page_count(page):
    text = await page.locator(
        "main > div > div:nth-child(2) > div > div > div > div"
    ).all_text_contents()
    return int(text[1].split(" ")[-1])


async def get_player_data(page):
    player_info_btns = page.locator(
        "main > div > div:nth-child(2) > div > div > table tbody tr > td:nth-child(1) > button:nth-child(1)"
    )

    for i in range(0, await player_info_btns.count()):
        await player_info_btns.nth(i).click()

        player_summary = await get_player_summary(page)
        await get_player_fixtures(page)

        await close_player_dialog(page)


async def get_player_summary(page):
    raw_player = (
        await page.locator(
            'div#root-dialog > div[role="presentation"] > dialog > div > div:nth-child(2) > div:nth-child(1)'
        ).all_inner_texts()
    )[0].split("\n")
    return parse_player(raw_player)


async def get_player_fixtures(page):
    section = (
        'div#root-dialog > div[role="presentation"] > dialog > div > div:nth-child(2)'
    )

    await page.locator(
        section + " > div:nth-child(2) > ul > li:nth-child(2) > a"
    ).click()
    # I'm not sure why, but the table is not loaded immediately for players that have been flagged
    await sleep(1)
    raw_fixtures = await page.locator(
        section
        + " > div:nth-child(2) > div:nth-child(2) > div > div > table:nth-child(2) > tbody"
    ).all_text_contents()

    start_idx = 0
    end_idx = raw_fixtures[0].index(")") + 2

    fixtures = []
    while start_idx < len(raw_fixtures[0]):
        # print(raw_fixtures[0][start_idx:end_idx])
        fixtures.append(parse_fixture(raw_fixtures[0][start_idx:end_idx]))
        start_idx = end_idx
        try:
            end_idx = raw_fixtures[0].index(")", start_idx) + 2
        except ValueError:
            break

    return fixtures


def parse_fixture(raw_fixture):
    space_count = 0
    fixture = {}

    # TODO: Figure out how to handle None and TBC
    if "\xa0" in raw_fixture:
        print(raw_fixture.split("\xa0"))

    for char in raw_fixture:
        if char == " ":
            space_count += 1

        if space_count < 3:
            set_or_append(fixture, "date", char)
        elif space_count < 4:
            if char != " " and (
                not fixture.get("time") or len(fixture.get("time")) <= 4
            ):
                set_or_append(fixture, "time", char)
            elif isinstance(try_parse_int(char), int) and (
                not fixture.get("gameweek") or len(fixture.get("gameweek")) <= 2
            ):
                set_or_append(fixture, "gameweek", char)
            elif char != " ":
                set_or_append(fixture, "opponent", char)
        else:
            if char == "(" or char == ")" or char == " ":
                continue
            elif not isinstance(try_parse_int(char), int):
                fixture["home_away"] = char
            else:
                fixture["difficulty"] = int(char)

    return fixture


def set_or_append(obj, key, value):
    if obj.get(key):
        obj[key] += value
    else:
        obj[key] = value


def try_parse_int(s):
    try:
        return int(s)
    except ValueError:
        return s


async def close_player_dialog(page):
    await page.locator(
        'div#root-dialog > div[role="presentation"] > dialog > div div:nth-child(1) button'
    ).click()


async def click_next_page(page):
    await page.locator(
        "main > div#root > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(5) > button:nth-child(4)"
    ).click()


def parse_player(raw_player):
    positions = ["Forward", "Midfielder", "Defender", "Goalkeeper"]
    is_flagged = raw_player[0] not in positions

    start_idx = 1 if is_flagged else 0
    end_idx = 24 if is_flagged else 23
    clean_player = raw_player[start_idx:end_idx]

    return {
        "position": clean_player[0],
        "name": clean_player[1],
        "team": clean_player[2],
        "price": float(clean_player[4][1 : len(clean_player[4]) - 1]),
        "form": float(clean_player[7]),
        "points_per_match": float(clean_player[9]),
        "gameweek_points": int(clean_player[12]),
        "total_points": int(clean_player[14]),
        "total_bonus": int(clean_player[16]),
        "ict_index": float(clean_player[18]),
        "tsb": float(clean_player[21][:-1]),
    }
