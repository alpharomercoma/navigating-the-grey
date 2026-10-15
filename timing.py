"""Times a scrape of every Robinsons mall directory (replayed) and prints the result."""
import json
import sys
import time

from malls import SLUGS


def duration(seconds):
    s = round(seconds, 1)
    m, s = divmod(s, 60)
    return f"{int(m)} min {s:04.1f} s" if m else f"{s:.1f} s"


def timed(scrape):
    started = time.perf_counter()
    rows = scrape(SLUGS)
    took = time.perf_counter() - started
    result = {"malls": len(SLUGS), "rows": len(rows), "seconds": round(took, 2),
              "malls_per_s": round(len(SLUGS) / took, 2), "python": sys.version.split()[0],
              "gil": getattr(sys, "_is_gil_enabled", lambda: True)()}
    if "--json" in sys.argv:
        print(json.dumps(result))
    else:
        print(f"{len(SLUGS)} malls, {len(rows):,} stores in {duration(took)}")
    return rows
