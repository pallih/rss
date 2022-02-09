from feedgen.feed import FeedGenerator
import requests
import json
import re

site_url = "https://testssl.manntal.is/leit/gogn/sofn/nyttsofn"
base_url = "http://skjalaskrar.skjalasafn.is/a/{}"

regex = r"<a href.*>(.*)</a>"


def scrape_site(url):
    r = requests.get(url)
    return r.json()


def make_feed(items):
    fg = FeedGenerator()
    fg.title("Skjalaskrár")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="http://skjalasafn.is", rel="alternate")
    fg.subtitle("Nýlega birt skjalasöfn í skjalaskrám Þjóðskjalasafns Íslands")
    fg.language("is")
    for item in items:
        fe = fg.add_entry()
        url = base_url.format(item["auðkenni"])
        matches = re.findall(regex, item["heiti"])
        fe.id(url)
        fe.title = matches[0]
        print(item["tímabil"])
        fe.description(" - ".join((matches[0], item["tímabil"])))
    fg.rss_file("rss/skjalaskrar.rss", pretty=True)


if __name__ == "__main__":
    items = scrape_site(site_url)
    feed = make_feed(items)
