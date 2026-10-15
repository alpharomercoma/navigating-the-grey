"""Record every Robinsons mall directory once, politely, for the speed benchmark.

    python record.py            # 53 pages, one a second: about 2 minutes

Each page is saved with how long the real site took to send it. replay.py serves these pages
back from your laptop with the same delays, so the benchmark hits Robinsons zero times.
Re-record from the network you'll present from: the delays are part of the result.
"""
import json
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "recordings" / "robinsons"
URL = "https://robinsonsmalls.com/mall-info/{slug}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; navigating-the-grey talk demo; alpharomercoma@proton.me)"}
GAP = 1.0  # seconds between requests


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    malls = json.loads((HERE / "robinsons_malls.json").read_text())
    timings = {}
    with requests.Session() as s:
        s.headers.update(HEADERS)
        for i, mall in enumerate(malls, 1):
            started = time.perf_counter()
            res = s.get(URL.format(slug=mall["slug"]), timeout=30)
            took = time.perf_counter() - started
            (OUT / f"{mall['slug']}.html").write_bytes(res.content)
            timings[mall["slug"]] = {"status": res.status_code, "seconds": round(took, 3),
                                     "bytes": len(res.content)}
            print(f"{i:>2}/{len(malls)}  {res.status_code}  {took:5.2f} s  {len(res.content) / 1000:6.1f} KB  {mall['slug']}")
            time.sleep(max(0.0, GAP - (time.perf_counter() - started)))
    (OUT / "timings.json").write_text(json.dumps(timings, indent=1))
    print(f"\nSaved {len(timings)} pages to {OUT}")


if __name__ == "__main__":
    main()
