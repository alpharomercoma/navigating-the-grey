"""What a limit looks like: hold a rate for a few seconds, raise it, and watch what comes back.

    python -m limits.ramp    # starts replay/server.py --capacity 20 on port 8801, ramps 4 to 40 requests/s

This only ever talks to a test server on your own machine, built to send at most 20 pages a second.
Healthy: every request becomes a page. Plateau: you send more and get no more, and pages come back
slower. Throttled: 429s, and fewer pages than before.

The plateau is a ceiling, not a budget. Never ramp someone else's site to find it: use their stated
limit, or start low and back off on slow answers, errors and Retry-After.
"""
import argparse
import asyncio
import json
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from common.malls import SLUGS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


async def hold(http, url, rate, seconds):
    results = []  # (status, latency, finished_at)

    async def one(n):
        started = time.perf_counter()
        try:
            async with http.get(url + SLUGS[n % len(SLUGS)]) as res:
                await res.read()
                results.append((res.status, time.perf_counter() - started, time.perf_counter()))
        except Exception:
            results.append((0, time.perf_counter() - started, time.perf_counter()))

    tasks, start = [], time.perf_counter()
    for i in range(round(rate * seconds)):
        await asyncio.sleep(max(0.0, start + i / rate - time.perf_counter()))
        tasks.append(asyncio.create_task(one(i + 1)))
    await asyncio.gather(*tasks)
    ok = [(t, done) for status, t, done in results if status == 200]
    # Pages per second, first page to last: queued pages that arrive after the send window count,
    # and so does the extra time they took.
    finished = sorted(done for _, done in ok)
    got = (len(finished) - 1) / (finished[-1] - finished[0]) if len(finished) > 1 else 0.0
    return {"sent_per_s": rate, "got_per_s": round(got, 1),
            "status_429": sum(s == 429 for s, _, _ in results), "status_503": sum(s == 503 for s, _, _ in results),
            "median_ms": round(statistics.median(t for t, _ in ok) * 1000) if ok else None}


async def ramp(url, rates, seconds, rest):
    rows = []
    async with ClientSession(connector=TCPConnector(limit=0), timeout=ClientTimeout(total=10)) as http:
        for rate in rates:
            row = await hold(http, url, rate, seconds)
            rows.append(row)
            print(f"sent {row['sent_per_s']:>3}/s   got {row['got_per_s']:>5}/s   "
                  f"429s {row['status_429']:>4}   503s {row['status_503']:>4}   "
                  f"median {row['median_ms'] or '-':>5} ms", flush=True)
            await asyncio.sleep(rest)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capacity", type=float, default=20)
    ap.add_argument("--start", type=int, default=4)
    ap.add_argument("--stop", type=int, default=40)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--seconds", type=float, default=6, help="how long to hold each rate")
    ap.add_argument("--rest", type=float, default=3, help="pause between rates")
    args = ap.parse_args()

    server = subprocess.Popen([sys.executable, "-m", "replay.server", "--port", "8801",
                               "--capacity", str(args.capacity)], cwd=ROOT, stdout=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen("http://127.0.0.1:8801/health", timeout=1).read()
                break
            except OSError:
                time.sleep(0.2)
        rates = list(range(args.start, args.stop + 1, args.step))
        rows = asyncio.run(ramp("http://127.0.0.1:8801/mall-info/", rates, args.seconds, args.rest))
    finally:
        server.terminate()
    plateau = max(r["got_per_s"] for r in rows)
    print(f"\nPlateau: about {plateau:.0f} pages/s on this test server. A ceiling, not a budget: on a real site,\n"
          "use their stated limit, or start low and back off on slow answers, errors and Retry-After.")
    (HERE / "ramp.json").write_text(json.dumps({"capacity": args.capacity, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
