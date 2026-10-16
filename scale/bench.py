"""Runs the five steps on every Robinsons mall (replayed) and saves the times for the slides.

    python -m replay.server &        # in another terminal, or let the bench start it
    python -m scale.bench            # about a minute
    python -m scale.bench --runs 3   # median of 3, as on the slides: writes scale/results.json
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from common.timing import duration

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PLAN = [  # module, label
    ("scale.step1_sync", "Sync, a for loop"),
    ("scale.step2_threads", "53 threads"),
    ("scale.step3_asyncio", "asyncio, all 53 at once"),
    ("scale.step4_processes", "53 processes"),
    ("scale.step5_hybrid", "A process per core, asyncio inside"),
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
    ap.add_argument("--out", default=str(HERE / "results.json"), help="where to save the times (default: the talk's scale/results.json)")
    ap.add_argument("--ft-python", help="a free-threaded Python 3.14t with requests and beautifulsoup4"
                    " (default: .venv-ft/bin/python if it exists)")
    args = ap.parse_args()

    server = None
    if not up():
        server = subprocess.Popen([sys.executable, "-m", "replay.server"], cwd=ROOT, stdout=subprocess.DEVNULL)
        while not up():
            time.sleep(0.2)

    plan = [(m, label, sys.executable) for m, label in PLAN]
    if not args.ft_python and (ROOT / ".venv-ft/bin/python").exists():
        args.ft_python = str(ROOT / ".venv-ft/bin/python")
    if args.ft_python:
        plan.append(("scale.step2_threads", "53 threads, Python 3.14t", args.ft_python))
    results = []
    try:
        for module, label, python in plan:
            runs = []
            for _ in range(args.runs):
                out = subprocess.run([python, "-m", module, "--json"], cwd=ROOT, check=True,
                                     capture_output=True, text=True).stdout
                runs.append(json.loads(out.strip().splitlines()[-1]))
            r = sorted(runs, key=lambda x: x["seconds"])[len(runs) // 2]
            r.update(module=module, label=label, runs=[x["seconds"] for x in runs])
            results.append(r)
            print(f"{label:<28} {duration(r['seconds']):>10}   {r['rows']:,} stores", flush=True)
    finally:
        if server:
            server.terminate()
    Path(args.out).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
