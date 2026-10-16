"""Robinsons, replayed on your laptop: every mall directory exactly as the real site sent it, after the
same delay it took. The speed benchmark hits this, never robinsonsmalls.com. Record first: replay/record_robinsons.py.

    python -m replay.server                 # http://127.0.0.1:8800/mall-info/robinsons-cybergate-davao
    python -m replay.server --capacity 20   # can only send 20 pages a second (for limits/ramp.py)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import statistics
import time
from collections import deque
from pathlib import Path

from aiohttp import web

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / "data" / "recordings" / "robinsons"


class Capacity:
    """A server that can only do so much: `rate` pages a second, then a queue, then 503s. Push past
    1.25x that and its firewall starts answering 429, more often the harder you push."""

    def __init__(self, rate: float, latency: float):
        self.slots = asyncio.Semaphore(max(1, round(rate * latency)))
        self.rate = rate
        self.recent: deque[float] = deque()
        self.rng = random.Random(7)

    def firewall(self) -> bool:
        now = time.monotonic()
        self.recent.append(now)
        while self.recent and self.recent[0] < now - 2:
            self.recent.popleft()
        seen = len(self.recent) / 2
        allowed = 1.25 * self.rate
        if seen <= allowed:
            return True
        return self.rng.random() > min(0.95, (seen - allowed) / allowed * 1.5)


def make_app(capacity: float | None) -> web.Application:
    timings = json.loads((REC / "timings.json").read_text())
    pages = {slug: (REC / f"{slug}.html").read_bytes() for slug in timings}
    delays = {slug: t["seconds"] for slug, t in timings.items()}
    median = statistics.median(delays.values())
    gate = None

    async def mall(request: web.Request) -> web.Response:
        nonlocal gate
        slug = request.match_info["slug"]
        if slug not in pages:
            raise web.HTTPNotFound()
        if capacity and gate is None:
            gate = Capacity(capacity, median)
        if gate is None:
            await asyncio.sleep(delays[slug])
            return web.Response(body=pages[slug], content_type="text/html", charset="utf-8")
        if not gate.firewall():
            return web.Response(status=429, text="Too Many Requests", headers={"Retry-After": "5"})
        try:
            await asyncio.wait_for(gate.slots.acquire(), timeout=1.0)
        except asyncio.TimeoutError:
            return web.Response(status=503, text="Service Unavailable")
        try:
            await asyncio.sleep(median)
            return web.Response(body=pages[slug], content_type="text/html", charset="utf-8")
        finally:
            gate.slots.release()

    async def health(_):
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_get("/mall-info/{slug}", mall)
    app.router.add_get("/health", health)
    return app


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8800)
    ap.add_argument("--capacity", type=float, help="pages a second the server can send (for limits/ramp.py)")
    args = ap.parse_args()
    if not (REC / "timings.json").exists():
        raise SystemExit("No recordings yet: run python -m replay.record_robinsons first.")
    print(f"Robinsons, replayed: http://127.0.0.1:{args.port}/mall-info/robinsons-cybergate-davao"
          + (f" ({args.capacity:g} pages/s at most)" if args.capacity else ""), flush=True)
    web.run_app(make_app(args.capacity), host="127.0.0.1", port=args.port,
                access_log=None, print=None, backlog=4096)


if __name__ == "__main__":
    main()
