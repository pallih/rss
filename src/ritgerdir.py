from feedgen.feed import FeedGenerator
import requests
import lxml.html

site_url = "https://skemman.is/simple-search?sort_by=dc.date.issued_dt&order=desc"
base_url = "https://skemman.is"


def scrape_site(url):
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    trs = root.xpath("//table[@class='t-data-grid']/tbody/tr")
    items = []
    for tr in trs:
        item = {}
        item["url"] = base_url + tr.xpath("td/a")[0].attrib["href"]
        item["title"] = tr.xpath("td/a")[0].text_content()
        item["description"] = tr.xpath("td[@headers='t3']")[0].text_content()
        items.append(item)
    return items


def make_feed(items):
    fg = FeedGenerator()
    fg.title("skemman.is")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="http://skemman.is", rel="alternate")
    fg.subtitle("Ritgerðir birtar á skemman.is")
    fg.language("is")
    for item in reversed(items):
        fe = fg.add_entry()
        fe.id(item["url"])
        fe.title(item["title"])
        fe.link(href=item["url"])
        fe.description(" - ".join((item["title"], item["description"])))
    fg.rss_file("rss/ritgerdir.rss", pretty=True)


if __name__ == "__main__":
    items = scrape_site(site_url)
    feed = make_feed(items)
