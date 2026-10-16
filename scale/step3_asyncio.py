"""Step 3, asyncio: one thread, every mall in flight at once. The event loop switches at every await.

Fine against the replay on your machine. Against a real site, the site's limit decides how many you send."""
import asyncio

import aiohttp

from common.malls import URL
from common.timing import timed
from doors.door1_robinsons import parse


async def scrape_mall(s, slug):
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
