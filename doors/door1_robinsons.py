"""Door 1: the stores are already in the HTML. requests fetches it, BeautifulSoup picks it apart.

    python -m doors.door1_robinsons
    python -m doors.door1_robinsons --replay    # no Wi-Fi: the same page, from replay/server.py
"""
import sys
import time

import requests
from bs4 import BeautifulSoup

from common.malls import LIVE, URL as REPLAY


def parse(html):
    """The loop from the slide, as a function the scale-up scripts reuse."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for li in soup.select("li.store-name"):
        name, _, phone = li.text.partition("|")
        rows.append({"name": name.strip(),
                     "phone": phone.strip()})
    return rows


if __name__ == "__main__":
    URL = REPLAY if "--replay" in sys.argv else LIVE

    # what the slide shows, line for line
    t = time.perf_counter()
    mall = "robinsons-cybergate-davao"
    html = requests.get(URL + mall).text
    took = time.perf_counter() - t
    soup = BeautifulSoup(html, "html.parser")

    rows = []
    for li in soup.select("li.store-name"):
        name, _, phone = li.text.partition("|")
        rows.append({"name": name.strip(),
                     "phone": phone.strip()})

    print(f"What comes back: {len(html.encode()) / 1000:.0f} KB of HTML in {took:.1f} s")
    li = soup.select_one("li.store-name")
    print(f'  <li class="... store-name {li["class"][2]}">{li.text.strip()}</li>\n')
    print(f"What we get: {len(rows)} dicts")
    for row in rows[:5]:
        print(" ", row)
