"""Sync vs async on three malls near Davao, timed per mall: the numbers on "Sync vs Async, Side by Side".

    python -m replay.server &        # the 53 recorded pages, on your laptop
    python -m scale.three_malls      # median of 7 runs each

For each mall: when the request went out, when the page was in hand, when it was parsed.
"""
import asyncio
import statistics
import time

import aiohttp
import requests

from common.malls import URL
from doors.door1_robinsons import parse

THREE = ["robinsons-cybergate-davao", "robinsons-place-tagum", "robinsons-place-gensan"]
RUNS = 7


def sync_run():
    t0, out = time.perf_counter(), []
    for slug in THREE:
        sent = time.perf_counter() - t0
        html = requests.get(URL + slug).text
        got = time.perf_counter() - t0
        parse(html)
        out.append((slug, sent, got, time.perf_counter() - t0))
    return out, time.perf_counter() - t0


async def async_run():
    t0, out = time.perf_counter(), {}
    async with aiohttp.ClientSession() as s:
        async def one(slug):
            sent = time.perf_counter() - t0
            res = await s.get(URL + slug)
            html = await res.text()
            got = time.perf_counter() - t0
            parse(html)
            out[slug] = (slug, sent, got, time.perf_counter() - t0)
        await asyncio.gather(*(one(slug) for slug in THREE))
    return [out[s] for s in THREE], time.perf_counter() - t0


def report(name, runs):
    total = statistics.median(t for _, t in runs)
    malls, _ = min(runs, key=lambda r: abs(r[1] - total))   # the run closest to the median
    print(f"{name}: 3 malls in {total:.2f} s (median of {len(runs)})")
    for slug, sent, got, parsed in malls:
        print(f"  {slug:<28} sent {sent:5.3f}  page in hand {got:5.3f}  parsed {parsed:5.3f} s")


if __name__ == "__main__":
    requests.get(URL + THREE[0]).text   # warm up
    report("Sync", [sync_run() for _ in range(RUNS)])
    report("Async", [asyncio.run(async_run()) for _ in range(RUNS)])
