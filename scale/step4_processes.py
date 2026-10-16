"""Step 4, processes: the thread code with one word changed. Each worker is its own Python,
so the parsing runs on every core. Each worker also costs a whole interpreter."""
from concurrent.futures import ProcessPoolExecutor

from common.timing import timed
from scale.step1_sync import scrape_mall  # unchanged


def scrape(slugs):
    with ProcessPoolExecutor(max_workers=32) as pool:
        parts = pool.map(scrape_mall, slugs)
        return [r for part in parts for r in part]


if __name__ == "__main__":    # needed: workers re-import this module
    timed(scrape)
