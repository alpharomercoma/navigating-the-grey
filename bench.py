"""Runs the four scrapers on every Robinsons mall (replayed) and saves the times for the slides.

    python replay.py &          # in another terminal, or let bench.py start it
    python bench.py             # about a minute
    python bench.py --runs 3    # median of 3, as on the slides
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from timing import duration

HERE = Path(__file__).resolve().parent
PLAN = [  # file, label
    ("scale_1_sync.py", "Sync, a for loop"),
    ("scale_2_threads.py", "32 threads"),
    ("scale_3_asyncio.py", "asyncio, 32 at once"),
    ("scale_4_processes.py", "32 processes"),
    ("scale_5_hybrid.py", "A process per core, asyncio inside"),
]


def up(url="http://127.0.0.1:8800/health"):
    try:
        urllib.request.urlopen(url, timeout=1).read()
        return True
    except OSError:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--ft-python", help="a free-threaded Python 3.14t with requests and beautifulsoup4"
                    " (default: .venv-ft/bin/python if it exists)")
    args = ap.parse_args()

    server = None
    if not up():
        server = subprocess.Popen([sys.executable, str(HERE / "replay.py")], stdout=subprocess.DEVNULL)
        while not up():
            time.sleep(0.2)

    plan = [(f, label, sys.executable) for f, label in PLAN]
    if not args.ft_python and (HERE / ".venv-ft/bin/python").exists():
        args.ft_python = str(HERE / ".venv-ft/bin/python")
    if args.ft_python:
        plan.append(("scale_2_threads.py", "32 threads, Python 3.14t", args.ft_python))
    results = []
    try:
        for file, label, python in plan:
            runs = []
            for _ in range(args.runs):
                out = subprocess.run([python, file, "--json"], cwd=HERE, check=True,
                                     capture_output=True, text=True).stdout
                runs.append(json.loads(out.strip().splitlines()[-1]))
            r = sorted(runs, key=lambda x: x["seconds"])[len(runs) // 2]
            r.update(file=file, label=label, runs=[x["seconds"] for x in runs])
            results.append(r)
            print(f"{label:<28} {duration(r['seconds']):>10}   {r['rows']:,} stores", flush=True)
    finally:
        if server:
            server.terminate()
    (HERE / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
