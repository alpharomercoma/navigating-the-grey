"""Scale 4, processes: the thread code with one word changed. Each worker is its own Python,
so the parsing runs on every core. Each worker also costs a whole interpreter."""
from concurrent.futures import ProcessPoolExecutor

from scale_1_sync import scrape_mall  # unchanged
from timing import timed


def scrape(slugs):
    with ProcessPoolExecutor(max_workers=32) as pool:
        parts = pool.map(scrape_mall, slugs)
        return [r for part in parts for r in part]


if __name__ == "__main__":    # needed: workers re-import this file
    timed(scrape)
