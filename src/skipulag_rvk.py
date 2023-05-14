import lxml.html
import requests
from feedgen.feed import FeedGenerator

site_url = "https://reykjavik.is/skipulag-i-kynningu"
base_url = "https://reykjavik.is{}"


def scrape_site(url):
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    wrappers = root.xpath("//div[@class='item-wrapper']")
    items = []
    for wrapper in wrappers:
        item = {}
        print(wrapper.text_content())
        item["address"] = wrapper.xpath("div/div[@class='group-left']/div/div/div/a")[
            0
        ].text
        item["url"] = wrapper.xpath("div/div[@class='group-left']/div/div/div/a")[
            0
        ].attrib["href"]
        item["type"] = wrapper.xpath("div/div[@class='group-middle']/div/div/div")[
            0
        ].text
        item["dates"] = wrapper.xpath("div/div[@class='group-right']/div/div/div")[
            0
        ].text_content()
        items.append(item)
    return items


def make_feed(items):
    fg = FeedGenerator()
    fg.title("Skipulag í kynningu - Reykjavík")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="http://skjalasafn.is", rel="alternate")
    fg.subtitle("Skipulag í kynningu - Reykjavík")
    fg.language("is")
    for item in items:
        fe = fg.add_entry()
        url = base_url.format(item["url"])
        fe.id(url)
        fe.title = item["address"]
        fe.link(href=url)
        fe.description(" - ".join((item["address"], item["type"], item["dates"])))
    fg.rss_file("rss/skipulag_rvk.rss", pretty=True)


if __name__ == "__main__":
    items = scrape_site(site_url)
    feed = make_feed(items)
