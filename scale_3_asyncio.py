"""Scale 3, asyncio: one thread, 32 malls in flight. The event loop switches at every await."""
import asyncio

import aiohttp

from door1_robinsons import parse
from malls import URL
from timing import timed

at_once = asyncio.Semaphore(32)           # 32 max


async def scrape_mall(s, slug):
    async with at_once:
        res = await s.get(URL + slug)
        return parse(await res.text())


async def main(slugs):
    async with aiohttp.ClientSession() as s:
        jobs = [scrape_mall(s, slug) for slug in slugs]
        return await asyncio.gather(*jobs)


def scrape(slugs):
    parts = asyncio.run(main(slugs))      # one list per mall
    return [r for part in parts for r in part]


if __name__ == "__main__":
    timed(scrape)
