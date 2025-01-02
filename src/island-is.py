import asyncio
import json
import re
from datetime import datetime

import aiohttp
import pytz  # Importing pytz to handle timezones
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from playwright.sync_api import sync_playwright


# Function to parse Icelandic date format like "4. desember 2024"
def parse_icelandic_date(date_str):
    months = {
        "janúar": 1,
        "febrúar": 2,
        "mars": 3,
        "apríl": 4,
        "maí": 5,
        "júní": 6,
        "júlí": 7,
        "ágúst": 8,
        "september": 9,
        "október": 10,
        "nóvember": 11,
        "desember": 12,
    }

    # Match date format like "4. desember 2024"
    match = re.match(r"(\d{1,2})\. (\w+) (\d{4})", date_str)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))

        # Convert the Icelandic month name to a month number
        month = months.get(month_name.lower(), 0)
        if month == 0:
            raise ValueError(f"Invalid month name: {month_name}")

        # Create a datetime object and set it to UTC timezone
        dt = datetime(year, month, day)
        # Set timezone to UTC
        return pytz.utc.localize(dt)

    raise ValueError(f"Invalid date format: {date_str}")


def generate_rss(org):
    print("Processing", org["slug"], org["link"])
    with sync_playwright() as p:
        extra_headers = {
            "sec-ch-ua": "'Not A(Brand';v='99', 'Google Chrome';v='121', 'Chromium';v='121'",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "accept-Language": "en-US,en;q=0.9",
        }

        browser = p.chromium.launch(headless=True)
        context = browser.new_context(extra_http_headers=extra_headers)
        page = context.new_page()

        try:
            url = org["link"]
            page.goto(url)

            page.wait_for_load_state("networkidle")

            evaluation = f"""Array.from(document.querySelectorAll('a[href^="/s/{org["slug"]}/frett/"]')).map(link =>
            {{const card = link.closest('div');
                    return {{
                        title: card.querySelector('h2')?.textContent.trim(),
                        link: link.href,
                        date: card.querySelector('p')?.textContent.trim(),
                        description: Array.from(card.querySelectorAll('p')).map(p => p.textContent).join(' ')
                    }};
                }})
            """
            news_items = page.evaluate(evaluation)

            print(f"Found {len(news_items)} items")

            fg = FeedGenerator()
            fg.title(f"{org["title"]} - Fréttir")
            fg.link(href=url)
            fg.description(f"{org["title"]} - Fréttir")
            fg.language("is")

            for item in news_items:
                fe = fg.add_entry()
                if item.get("title"):
                    fe.title(item["title"])
                if item.get("link"):
                    fe.link(href=item["link"])
                if item.get("date"):
                    try:
                        fe.published(parse_icelandic_date(item["date"]))
                    except:
                        fe.published(datetime.now(pytz.utc))
                if item.get("description"):
                    # Remove date from the beginning of the description
                    cleaned_description = re.sub(
                        r"^\d{1,2}\. \w+ \d{4}\s*", "", item["description"]
                    ).strip()
                    fe.description(cleaned_description)

            fg.rss_file(f"rss/island_is/{org["slug"]}.rss")

        finally:
            browser.close()


async def fetch_head(session, url):
    async with session.head(url) as response:
        return response


async def process_organizations(orgs):
    organizations = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for org in orgs:
            organization = {"slug": org["slug"], "title": org["title"]}
            url = f"https://island.is/s/{org['slug']}/frett"
            tasks.append((organization, fetch_head(session, url)))

        responses = await asyncio.gather(*[task for _, task in tasks])

        for (organization, _), response in zip(tasks, responses):
            if response.status == 200:
                # print(organization["slug"], organization["title"], org["link"])
                organization["link"] = str(response.url)
                organizations.append(organization)
    return organizations


def find_slugs():
    r = requests.get("https://island.is/s")
    soup = BeautifulSoup(r.text, "lxml")
    script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
    if script_tag:
        json_content = script_tag.string
        data = None
        try:
            # Load the JSON content into a Python dictionary
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    else:
        print("Script tag with id='__NEXT_DATA__' not found.")
    if data:
        organizations = []
        orgs = data["props"]["pageProps"]["pageProps"]["pageProps"]["componentProps"][
            "organizations"
        ]["items"]
        organizations = asyncio.run(process_organizations(orgs))
    if organizations:
        print(len(organizations), "organizations found")
        with open("rss/island_is/organizations.json", "w", encoding="utf-8") as f:
            json.dump(organizations, f, ensure_ascii=False, indent=4)
        return organizations
    return None


if __name__ == "__main__":
    organizations = find_slugs()
    if organizations:
        for org in organizations:
            generate_rss(org)
