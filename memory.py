"""What one worker costs in memory: the "Each worker adds" row on "Threads vs Processes". Linux only (/proc).

    python memory.py

Threads: how much the process's resident memory grows per idle thread.
Processes: each worker's resident memory (RSS) and its own, unshared memory (USS), for every start method.
"""
import multiprocessing as mp
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from door1_robinsons import parse

PAGE = Path(__file__).resolve().parent / "recordings/robinsons/robinsons-place-manila.html"


def rss_kb(pid="self"):
    for line in open(f"/proc/{pid}/status"):
        if line.startswith("VmRSS"):
            return int(line.split()[1])


def uss_kb(pid):
    own = 0
    for line in open(f"/proc/{pid}/smaps_rollup"):
        key, value = line.split()[:2]
        if key in ("Private_Clean:", "Private_Dirty:"):
            own += int(value)
    return own


def per_thread_kb(n=32):
    hold = threading.Event()
    before = rss_kb()
    threads = [threading.Thread(target=hold.wait) for _ in range(n)]
    for t in threads:
        t.start()
    time.sleep(0.5)
    after = rss_kb()
    hold.set()
    for t in threads:
        t.join()
    return (after - before) / n


def work(_):
    parse(PAGE.read_text(encoding="utf-8"))   # each worker parses one real page
    time.sleep(1.0)                            # and stays alive while we measure


def per_process(method, n=32):
    with ProcessPoolExecutor(n, mp_context=mp.get_context(method)) as pool:
        jobs = [pool.submit(work, i) for i in range(n)]
        time.sleep(0.8)
        pids = [p.pid for p in pool._processes.values()]
        rss = [rss_kb(p) / 1024 for p in pids]
        uss = [uss_kb(p) / 1024 for p in pids]
        for j in jobs:
            j.result()
    return rss, uss


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}, {os.cpu_count()} cores")
    print("Each idle thread adds:", ", ".join(f"{per_thread_kb():.0f} KB" for _ in range(3)))
    for method in ("fork", "forkserver", "spawn"):
        rss, uss = per_process(method)
        print(f"{method:<10} each worker: {statistics.median(uss):4.1f} MB of its own "
              f"({min(uss):.1f}-{max(uss):.1f}), {statistics.median(rss):4.1f} MB resident ({min(rss):.1f}-{max(rss):.1f})")
