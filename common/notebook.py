"""What navigating_the_grey.ipynb shares between its parts: one User-Agent, local servers, a text timeline,
and the scoreboard for Part 2."""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Say who you are. Put your own name or email in here if you keep using this.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; navigating-the-grey notebook; PyCon Davao 2026)"}

_servers = {}


def server_up(port):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1).read()
        return True
    except OSError:
        return False


def ensure_server(script, port):
    """Start `script --port port` in the background unless something already answers there.
    `script` is a module, such as replay.server, or a file."""
    if not server_up(port):
        target = [script] if script.endswith(".py") else ["-m", script]
        _servers[port] = subprocess.Popen([sys.executable, *target, "--port", str(port)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            if server_up(port):
                break
            time.sleep(0.2)
    return server_up(port)


def ensure_replay():
    """replay/server.py: the 53 recorded Robinsons pages, on port 8800."""
    return ensure_server("replay.server", 8800)


def timeline(log, start, step=0.02):
    """Print one line per mall: ░ waiting for the page, █ parsing it. One character = `step` seconds."""
    width = max(len(slug.replace("robinsons-", "")) for slug, *_ in log)
    for slug, sent, got, parsed in sorted(log, key=lambda row: row[1:]):
        a, b, c = (round((x - start) / step) for x in (sent, got, parsed))
        bar = " " * a + "░" * max(b - a, 1) + "█" * max(c - b, 1)
        name = slug.replace("robinsons-", "")
        print(f"{name:<{width}}  {bar:<75} {(got - sent) * 1000:4.0f} ms waiting, "
              f"{(parsed - got) * 1000:3.0f} ms parsing")
    print(f"{'':<{width}}  ░ waiting  █ parsing   (one character = {step * 1000:.0f} ms)")


def _s(seconds, unit="s"):
    return f"{seconds + 1e-9:.1f}{unit}"  # round half up, like the slides


# ---------------------------------------------------------------- the Part 2 scoreboard
ORDER = ["Sync, a for loop", "53 threads", "asyncio, all 53 at once", "53 processes",
         "A process per core, asyncio inside"]
BONUS = "53 threads, Python 3.14t"         # not on the slides; shown once its cell has run
SHOWN = {"A process per core, asyncio inside": f"{os.cpu_count()} processes + asyncio",
         "53 threads, Python 3.14t": "53 threads on 3.14t"}
_board = {}


def _talk(path="scale/results.json"):
    return {r["label"]: r["seconds"] for r in json.loads(Path(path).read_text())}


def record(label, seconds, rows):
    """Put one run on the scoreboard and print it next to the slide's number."""
    _board[label] = seconds
    talk = _talk().get(label)
    where = "talk's machine" if label == BONUS else "slide"
    print(f"{SHOWN.get(label, label)}: all 53 malls, {rows:,} stores in {_s(seconds, ' s')}"
          + (f"   ({where}: {_s(talk, ' s')})" if talk else ""))


def score(label, started, pages):
    """`pages`: what the scrape returned, one list of stores per mall (or per worker)."""
    record(label, time.perf_counter() - started, sum(len(p) for p in pages))


def scoreboard():
    """Every run so far, next to the talk's numbers (median of 3, a 2-core machine, 17 Oct 2026)."""
    talk = _talk()
    loop = _board.get(ORDER[0]) or talk[ORDER[0]]
    print(f"{'all 53 malls':<26}{'here':>8}{'slide':>8}{'vs loop':>9}")
    rows = ORDER + ([BONUS] if BONUS in _board else [])
    for label in rows:
        mine, theirs = _board.get(label), (None if label == BONUS else talk.get(label))
        if mine is None:
            print(f"{SHOWN.get(label, label):<26}{'·':>8}{(_s(theirs) if theirs else '-'):>8}")
            continue
        bar = "█" * max(1, round(mine / loop * 40))
        print(f"{SHOWN.get(label, label):<26}{_s(mine):>8}{(_s(theirs) if theirs else '-'):>8}"
              f"{loop / mine:>8.0f}x  {bar}")
    print(f"\nHere: one run each, on {os.cpu_count()} cores. You can't finish before the slowest page: "
          "Opus Mall alone took 1.95 s.")


def show_results(path="my_results.json", talk="scale/results.json"):
    """Your scale/bench.py results next to the talk's (17 Oct, a 2-core cloud machine)."""
    mine = json.loads(Path(path).read_text())
    theirs = _talk(talk)
    loop = next(r["seconds"] for r in mine if r["module"] == "scale.step1_sync")
    print(f"{'all 53 malls':<36}{'yours':>8}{'talk':>8}{'vs loop':>9}")
    for r in mine:
        talk_s = theirs.get(r["label"])
        bar = "█" * max(1, round(r["seconds"] / loop * 40))
        print(f"{r['label']:<36}{_s(r['seconds']):>8}{(_s(talk_s) if talk_s else '-'):>8}"
              f"{loop / r['seconds']:>8.0f}x  {bar}")
    print(f"\n{mine[0]['rows']:,} stores each time. Talk numbers: median of 3 runs on 17 Oct 2026.")
