import requests
import csv
from feedgen.feed import FeedGenerator
import codecs


sheet_id = "1O37mhN5bMt5nd-CaO7ue_3KMbip6eVETWKXwfILsf3E"
sheet_name = "Beställt"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"


def make_feed(url):
    fg = FeedGenerator()
    fg.title("Palmemordsarkivet.se")
    fg.author({"name": "Páll Hilmarsson", "email": "pallih@gogn.in"})
    fg.link(href="Palmemordsarkivet.se", rel="alternate")
    fg.subtitle("Nýlega birt skjöl úr morðrannsókninni á Olof Palme")
    fg.language("is")
    r = requests.get(url)
    lines = codecs.iterdecode(r.iter_lines(), "utf-8")
    next(lines)
    reader = csv.DictReader(lines, delimiter=",")
    rows = list(reader)
    for row in rows[-50:]:
        if not row["Titel"]:
            continue
        fe = fg.add_entry()
        url = row["Länk till kopia"]
        fe.id(url)
        fe.title = row["Titel"]
        fe.link(href=url)
        fe.description(row["Titel"])
    fg.rss_file("rss/palmemordsarkivet.rss", pretty=True)


if __name__ == "__main__":
    make_feed(sheet_url)
