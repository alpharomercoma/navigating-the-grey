"""Scale 1, sync: one mall at a time. The CPU idles through every wait."""
import requests

from door1_robinsons import parse
from malls import URL
from timing import timed


def scrape_mall(slug):
    html = requests.get(URL + slug).text
    return parse(html)          # door 1's loop


def scrape(slugs):
    rows = []
    for slug in slugs:
        rows += scrape_mall(slug)
    return rows


if __name__ == "__main__":
    timed(scrape)
