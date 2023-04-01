import lxml.html
import requests
from feedgen.feed import FeedGenerator

site_url = "https://island.is/s/landskjorstjorn/fundargerdir-landskjorstjornar"
base_url = "https://island.is"


def scrape_site(url):
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    h3s = root.xpath("//h3")
    items = []
    for h3 in h3s:
        item = {}
        item["url"] = site_url
        item["title"] = h3.text_content()
        item["description"] = item["title"]
        item["issuer"] = "Landskjörstjórn"
        items.append(item)
    return items


def make_feed(items):
    fg = FeedGenerator()
    fg.title("Fundargerðir Landskjörstjórnar")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="https://island.is/s/landskjorstjorn/", rel="alternate")
    fg.subtitle("Fundargerðir Landskjörstjórnar á island,is")
    fg.language("is")
    for item in items:
        fe = fg.add_entry()
        fe.id(item["title"])
        fe.title(" - ".join((item["title"], item["issuer"])))
        fe.link(href=item["url"])
        fe.description(item["description"])
    fg.rss_file("rss/landskjorstjorn.rss", pretty=True)


if __name__ == "__main__":
    items = scrape_site(site_url)
    feed = make_feed(items)
