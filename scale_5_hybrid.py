"""Scale 5, the production pattern: one asyncio loop per CPU core. Waits overlap in each loop,
and every core parses."""
import asyncio
import os
from concurrent.futures import ProcessPoolExecutor

from scale_3_asyncio import main
from timing import timed

N = os.cpu_count()


def shard(slugs):               # every Nth mall
    parts = asyncio.run(main(slugs))
    return [r for part in parts for r in part]


def scrape(slugs):
    with ProcessPoolExecutor(N) as pool:
        parts = pool.map(shard, [slugs[k::N] for k in range(N)])
        return [r for part in parts for r in part]


if __name__ == "__main__":
    timed(scrape)
