"""Step 2, threads: one thread per mall, so all 53 wait together. Parsing still takes turns (the GIL)."""
from concurrent.futures import ThreadPoolExecutor

from common.timing import timed
from scale.step1_sync import scrape_mall  # unchanged


def scrape(slugs):
    with ThreadPoolExecutor(max_workers=len(slugs)) as pool:   # one thread per mall
        parts = pool.map(scrape_mall, slugs)
        return [r for part in parts for r in part]


if __name__ == "__main__":
    timed(scrape)
