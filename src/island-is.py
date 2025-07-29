import asyncio
import json
import os
import re
from datetime import datetime

import aiohttp
import pytz
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


def parse_iso_date(date_str: str) -> datetime:
    """Parse an ISO-ish YYYY-MM-DD date into a timezone‐aware UTC datetime."""
    dt = datetime.fromisoformat(date_str)
    return pytz.utc.localize(dt)


def fetch_news_list(org_slug: str):
    """
    Fetch the Next.js JSON blob from /s/{org_slug}/frett
    and return the ['date','title','slug'] list.
    """
    url = f"https://island.is/s/{org_slug}/frett"
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    data = json.loads(script.string)

    # drill into componentProps.newsList
    page = data["props"]["pageProps"]["pageProps"]["pageProps"]["page"]
    component = page["props"]["componentProps"]
    news_list = component.get("newsList", [])

    # each item has 'date','title','slug'
    return news_list


def generate_rss(org):
    """
    Given {'slug': ..., 'title': ..., 'link': ...},
    fetch its newsList and write an RSS file.
    """
    print(f"Generating RSS for {org['slug']}…", end=" ")

    news_items = fetch_news_list(org["slug"])
    out_dir = "rss/island_is"
    os.makedirs(out_dir, exist_ok=True)

    fg = FeedGenerator()
    fg.title(f"{org['title']} – Fréttir")
    fg.link(href=org["link"], rel="alternate")
    fg.description(f"{org['title']} – Fréttir")
    fg.language("is")

    for item in news_items:
        fe = fg.add_entry()
        fe.title(item["title"])
        # build the full link
        fe.link(href=f"https://island.is/s/{org['slug']}/frett/{item['slug']}")
        # parse & set published date
        try:
            fe.published(parse_iso_date(item["date"]))
        except Exception:
            fe.published(datetime.now(pytz.utc))
    # write out
    out_path = f"rss/island_is/{org['slug']}.rss"
    fg.rss_file(out_path)
    print(f"wrote {len(news_items)} items to {out_path}")


async def fetch_head(session, url):
    async with session.head(url) as resp:
        return resp


async def discover_orgs(raw_orgs):
    valid = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for org in raw_orgs:
            url = f"https://island.is/s/{org['slug']}/frett"
            tasks.append((org, fetch_head(session, url)))
        results = await asyncio.gather(*[t for _, t in tasks])
        for (org, _), resp in zip(tasks, results):
            if resp.status == 200:
                valid.append({"slug": org["slug"], "title": org["title"], "link": str(resp.url)})
    return valid


def find_slugs():
    r = requests.get("https://island.is/s")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find("script", id="__NEXT_DATA__", type="application/json")
    data = json.loads(script.string)

    raw = data["props"]["pageProps"]["pageProps"]["pageProps"]["componentProps"]["organizations"]["items"]
    orgs = asyncio.run(discover_orgs(raw))
    print(f"{len(orgs)} valid organizations found")
    os.makedirs("rss/island_is", exist_ok=True)
    # with open("rss/island_is/organizations.json", "w", encoding="utf-8") as f:
    #     json.dump(orgs, f, ensure_ascii=False, indent=2)
    return orgs


if __name__ == "__main__":
    orgs = find_slugs()
    for org in orgs:
        generate_rss(org)
