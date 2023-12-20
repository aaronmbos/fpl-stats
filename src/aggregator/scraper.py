from asyncio import sleep
from playwright.async_api import async_playwright
import logging.config
from database import insert_players, swap_collections


logger = logging.getLogger(__name__)
logging.config.fileConfig("./logging_config/dev.ini")


async def scrape():
    # How will I determine if data should be scraped?
    # Let's just run it everyday at midnight
    # Each run will overwrite the previous data
    # Plan for overwriting entire dataset will be to insert into temp collection, then swap and delete previous
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://fantasy.premierleague.com/statistics")

        await accept_cookies(page)

        page_count = await get_page_count(page)

        for page_idx in range(0, page_count):
            player_data = await get_player_data_for_page(page)
            insert_players(player_data)

            logger.info("Collected player data from page %s.", page_idx + 1)

            if page_idx < page_count - 1:
                await click_next_page(page)

        swap_collections()

        await browser.close()


async def accept_cookies(page):
    await page.locator("button#onetrust-accept-btn-handler").click()
    logger.info("Cookies accepted.")


async def get_page_count(page):
    text = await page.locator(
        "main > div > div:nth-child(2) > div > div > div > div"
    ).all_text_contents()

    page_count = int(text[1].split(" ")[-1])
    logger.info("Found %s pages of player data.", page_count)

    return page_count


async def get_player_data_for_page(page):
    player_info_btns = page.locator(
        "main > div > div:nth-child(2) > div > div > table tbody tr > td:nth-child(1) > button:nth-child(1)"
    )

    player_data = []
    for i in range(0, await player_info_btns.count()):
        await player_info_btns.nth(i).click()

        player_summary = await get_player_summary(page)
        player_season_stats = await get_season_stats(page)
        player_history = await retry(get_player_history, page)
        ## Since fixtures requires a click, gather after stats and history
        player_fixtures = await retry(get_player_fixtures, page)

        player_summary["season_stats"] = player_season_stats
        player_summary["history"] = player_history
        player_summary["fixtures"] = player_fixtures

        player_data.append(player_summary)

        await close_player_dialog(page)

    return player_data


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

    raw_fixtures = await page.locator(
        section
        + " > div:nth-child(2) > div:nth-child(2) > div > div > table:nth-child(2) > tbody"
    ).all_text_contents()

    start_idx = 0
    end_idx = raw_fixtures[0].index(")") + 2

    fixtures = []
    while start_idx < len(raw_fixtures[0]):
        fixtures.extend(parse_fixture(raw_fixtures[0][start_idx:end_idx]))
        start_idx = end_idx
        try:
            end_idx = raw_fixtures[0].index(")", start_idx) + 2
        except ValueError:
            break

    return fixtures


async def get_season_stats(page):
    gw_stats = await retry(get_gameweek_stats, page)
    totals = await retry(get_season_stat_totals, page)
    return {
        "gameweek_stats": gw_stats,
        "aggregate_stats": totals,
    }


async def get_season_stat_totals(page):
    [raw_totals, raw_per_ninety] = await page.evaluate(
        "() => {var stats = [];document.querySelectorAll('div#root-dialog > div[role=\"presentation\"] > dialog > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(1) > div:nth-child(2) > table > tfoot > tr').forEach((row, idx) => {stats.push([]); row.children.forEach(cell => stats[idx].push(cell.textContent))}); return stats;}"
    )
    # TODO: Need to parse these raw values
    return {
        "season_totals": parse_season_totals(raw_totals),
        "stats_per_ninety": parse_per_ninety_stats(raw_per_ninety),
    }


def parse_season_totals(raw_totals):
    return {"raw": raw_totals}


def parse_per_ninety_stats(raw_per_ninety):
    return {"raw": raw_per_ninety}


async def get_gameweek_stats(page):
    raw_gameweek_stats = await page.evaluate(
        "() => {var stats = [];document.querySelectorAll('div#root-dialog > div[role=\"presentation\"] > dialog > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(1) > div:nth-child(2) > table > tbody > tr').forEach((row, idx) => {stats.push([]); row.children.forEach(cell => stats[idx].push(cell.textContent))}); return stats;}"
    )

    if raw_gameweek_stats == []:
        raise Exception("No gameweek stats found")

    return parse_gameweek_stats(raw_gameweek_stats)


def parse_gameweek_stats(raw_gameweek_stats):
    parsed_gw_stats = []
    for gw in raw_gameweek_stats:
        parsed_gw_stats.append(
            {
                "gameweek": int(gw[0]),
                "opponent": gw[1].strip(),
                "outcome": gw[2],
                "points": int(gw[3]),
                "start": int(gw[4]),
                "minutes_played": int(gw[5]),
                "goals_scored": int(gw[6]),
                "assists": int(gw[7]),
                "expected_goals": float(gw[8]),
                "expected_assists": float(gw[9]),
                "expected_goal_involvements": float(gw[10]),
                "clean_sheets": int(gw[11]),
                "goals_conceded": int(gw[12]),
                "expected_goals_conceded": float(gw[13]),
                "own_goals": int(gw[14]),
                "penalties_saved": int(gw[15]),
                "penalties_missed": int(gw[16]),
                "yellow_cards": int(gw[17]),
                "red_cards": int(gw[18]),
                "saves": int(gw[19]),
                "bonus_points": int(gw[20]),
                "bonus_points_system": int(gw[21].replace(",", "")),
                "influence": float(gw[22]),
                "creativity": float(gw[23]),
                "threat": float(gw[24]),
                "ict_index": float(gw[25]),
                "nt": int(gw[26]),
                "sb": int(gw[27]),
                "price": float(gw[28][1 : len(gw[28]) - 1]),
            }
        )
    return parsed_gw_stats


# TODO: This is returning the full dataset of gameweek and history, need to get just history
async def get_player_history(page):
    raw_stat_history = await page.evaluate(
        "() => {var stats = [];document.querySelectorAll('div#root-dialog > div[role=\"presentation\"] > dialog > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > table > tbody > tr').forEach((row, idx) => {stats.push([]); row.children.forEach(cell => stats[idx].push(cell.textContent))}); return stats;}"
    )

    if len(raw_stat_history) == 0:
        return []

    return parse_player_history(raw_stat_history)


def parse_player_history(raw_stat_history):
    parsed_stats = []
    for row in raw_stat_history:
        parsed_stats.append(
            {
                "season": row[0],
                "points": int(row[1]),
                "games_started": int(row[2]),
                "minutes_played": int(row[3].replace(",", "")),
                "goals_scored": int(row[4]),
                "assists": int(row[5]),
                "expected_goals": float(row[6]),
                "expected_assists": float(row[7]),
                "expected_goal_involvements": float(row[8]),
                "clean_sheets": int(row[9]),
                "goals_conceded": int(row[10]),
                "expected_goals_conceded": float(row[11]),
                "own_goals": int(row[12]),
                "penalties_saved": int(row[13]),
                "penalties_missed": int(row[14]),
                "yellow_cards": int(row[15]),
                "red_cards": int(row[16]),
                "saves": int(row[17]),
                "bonus_points": int(row[18]),
                "bonus_points_system": int(row[19].replace(",", "")),
                "influence": float(row[20]),
                "creativity": float(row[21]),
                "threat": float(row[22]),
                "ict_index": float(row[23]),
                "season_start_price": float(row[24][1 : len(row[24]) - 1]),
                "season_end_price": float(row[25][1 : len(row[25]) - 1]),
            }
        )
    return parsed_stats


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


def parse_fixture(raw_fixture):
    # This could probably be done more elegantly by evaluating JS
    space_count = 0
    fixture = {}

    if "\xa0" in raw_fixture:
        [none_gameweek, fixture_gameweek] = raw_fixture.split("\xa0")[1:3]
        return [
            {"gameweek": int(none_gameweek.split("None")[0]), "opponent": "None"},
            parse_fixture(fixture_gameweek),
        ]
    elif "TBC" in raw_fixture:
        [opponent, details] = raw_fixture.split(" ")
        opponent = opponent[3:]
        home_away = details[1]
        difficulty = int(details[-1])
        return [
            {
                "gameweek": "TBC",
                "opponent": opponent,
                "home_away": home_away,
                "difficulty": difficulty,
            }
        ]

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

    return [fixture]


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


async def retry(func, *args):
    for i in range(10):
        try:
            return await func(*args)
        except Exception as e:
            logger.warning(f"Failed attempt {i+1} of {5}: {e}")
            await sleep(0.2 * i)
            continue
    raise Exception(f"Function {func.__name__} failed after {5} retries")
