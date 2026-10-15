"""Save Megaworld's Uptown Mall page and its store API once, so doors 2 and 3 have a fallback.

    python record_megaworld.py      # 4 requests, a second apart

door2_megaworld.py --replay and door3_megaworld_api.py --replay read these files instead of the
network. Use them only if the venue Wi-Fi fails; the live run is the point of the demo.
"""
import json
import time
from pathlib import Path

import requests

from door2_megaworld import URL
from door3_megaworld_api import API, ENV, KEYS, UPTOWN_MALL

HERE = Path(__file__).resolve().parent
OUT = HERE / "recordings" / "megaworld"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; navigating-the-grey talk demo; alpharomercoma@proton.me)"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with requests.Session() as s:
        s.headers.update(HEADERS)
        shell = s.get(URL, timeout=30)
        (OUT / "uptown-mall.html").write_bytes(shell.content)
        print(f"uptown-mall.html  {len(shell.content) / 1000:.1f} KB")
        skip, n = 0, 100
        while n == 100:
            time.sleep(1)
            q = {"environment": ENV, "limit": 100, "query": UPTOWN_MALL, "skip": skip}
            entries = s.get(API, params=q, headers=KEYS, timeout=30).json()["entries"]
            (OUT / f"tenants-{skip}.json").write_text(json.dumps({"entries": entries}, ensure_ascii=False))
            print(f"tenants-{skip}.json  {len(entries)} stores")
            n, skip = len(entries), skip + len(entries)
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()
