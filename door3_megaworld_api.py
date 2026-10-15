"""Door 3: the page's own API. Megaworld's page asks a CMS for its stores; ask it yourself.

    python door3_megaworld_api.py
    python door3_megaworld_api.py --replay    # no Wi-Fi: the responses record_megaworld.py saved
"""
import json
import sys
import time
from pathlib import Path

API = "https://cdn.contentstack.io/v3/content_types/tenant/entries/"
ENV = "prod-environment"
UPTOWN_MALL = '{"reference": {"$in_query": {"name": "Uptown Mall"}}}'
# Megaworld's public, read-only delivery keys: the site sends them to every visitor's browser.
KEYS = {"api_key": "blt827157d7af7bc6d4", "access_token": "cs12c8f62754c81457af4cc5fc"}

SAVED = Path(__file__).resolve().parent / "recordings" / "megaworld"

if "--replay" in sys.argv:
    class requests:  # same call, answered from disk
        @staticmethod
        def get(url, params, headers):
            class Saved:
                def json(self):
                    return json.loads((SAVED / f"tenants-{params.get('skip', 0)}.json").read_text())
            return Saved()
    print("(replayed from recordings/megaworld)")
else:
    import requests

if __name__ == "__main__":
    # what the slide shows, line for line
    t = time.perf_counter()
    q = {"environment": ENV, "limit": 100,
         "query": UPTOWN_MALL}
    data = requests.get(API, params=q,
                        headers=KEYS).json()
    rows = data["entries"]     # 100 stores
    took = time.perf_counter() - t

    print(f"What comes back: JSON in {took:.1f} s, {len(rows)} stores in one request")
    r = rows[0]
    print(" ", json.dumps({k: r[k] for k in ("name", "category", "shop_type", "floor")}, ensure_ascii=False))

    # the whole mall: keep asking until a page comes back short
    everything, skip = list(rows), len(rows)
    while len(rows) == 100:
        time.sleep(0 if "--replay" in sys.argv else 1)   # politely
        rows = requests.get(API, params=q | {"skip": skip}, headers=KEYS).json()["entries"]
        everything += rows
        skip += len(rows)
    print(f"\nAll of Uptown Mall: {len(everything)} stores in {-(-len(everything) // 100)} requests")
