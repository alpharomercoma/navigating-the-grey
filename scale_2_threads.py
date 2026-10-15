"""Scale 2, threads: 32 malls in flight, waiting together. Parsing still takes turns (the GIL)."""
from concurrent.futures import ThreadPoolExecutor

from scale_1_sync import scrape_mall  # unchanged
from timing import timed


def scrape(slugs):
    with ThreadPoolExecutor(max_workers=32) as pool:
        parts = pool.map(scrape_mall, slugs)
        return [r for part in parts for r in part]


if __name__ == "__main__":
    timed(scrape)
