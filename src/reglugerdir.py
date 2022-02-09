from feedgen.feed import FeedGenerator
import requests
import lxml.html

site_url = "https://island.is/reglugerdir"
base_url = "https://island.is"


def scrape_site(url):
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    divs = root.xpath(
        "//div[@class='inlbuo0 _18ovwg513u _18ovwg5141 _18ovwg5iz _18ovwg5jy _18ovwg5145 _15jbcqsnr _15jbcqs26 _15jbcqs4c _15jbcqs8o']"
    )
    items = []
    for div in divs:
        item = {}
        item["url"] = base_url + div.xpath("a")[0].attrib["href"]
        item["title"] = div.xpath("a/div/div/h3")[0].text_content()
        item["description"] = div.xpath("a/div/div/p")[0].text_content()
        item["issuer"] = div.xpath("a/div/div/div//span")[0].text_content()
        items.append(item)
    return items


def make_feed(items):
    fg = FeedGenerator()
    fg.title("Reglugerðir")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="http://reglugerdir.is", rel="alternate")
    fg.subtitle("Settar reglugerðir birtar á island.is")
    fg.language("is")
    for item in items:
        fe = fg.add_entry()
        fe.id(item["url"])
        fe.title(" - ".join((item["title"], item["issuer"])))
        fe.link(href=item["url"])
        fe.description(item["description"])
    fg.rss_file("rss/reglugerdir.rss", pretty=True)


if __name__ == "__main__":
    items = scrape_site(site_url)
    feed = make_feed(items)
