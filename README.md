# Navigating the Grey: talk code

The demos and benchmarks from the PyCon Davao 2026 talk
*Navigating the Grey: Building Resilient Python Scrapers That Survive at Scale*.

**No setup? Run every demo in your browser:**
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alpharomercoma/navigating-the-grey/blob/main/navigating_the_grey.ipynb)
It's the talk's live demos, step by step: the three doors; 53 malls with a for loop, asyncio, threads,
processes and both, on a scoreboard next to the slides' numbers; SM direct and through your own proxies.
A bonus part, not run on stage, makes the requests inside PengePassportPH by hand before the package
makes them. The notebook carries the recorded pages with it, so the speed demos never touch Robinsons,
and the passport part runs against a local stand-in unless you tick LIVE.

Also from the talk:

- PengePassportPH: [alphaexperiments.com/p3h](https://alphaexperiments.com/p3h) ·
  [github.com/alpharomercoma/penge-passport-ph](https://github.com/alpharomercoma/penge-passport-ph)
- Philippine Mall Explorer: [alpharomercoma.github.io/philippine-mall-explorer](https://alpharomercoma.github.io/philippine-mall-explorer) ·
  [github.com/alpharomercoma/philippine-mall-explorer](https://github.com/alpharomercoma/philippine-mall-explorer)

Two real Philippine mall sites, three ways to read them:

| Door | Site | What comes back | Script |
|---|---|---|---|
| 1 | robinsonsmalls.com/mall-info/robinsons-cybergate-davao | The stores are in the HTML | `door1_robinsons.py` (requests + BeautifulSoup) |
| 2 | megaworld-lifestylemalls.com/malls/uptown-mall | An empty page that JavaScript fills | `door2_megaworld.py` (Playwright) |
| 3 | cdn.contentstack.io/…/tenant/entries | The JSON the page fetches | `door3_megaworld_api.py` (requests `.json()`) |

Both sites allow bots in robots.txt. Ayala's says `Disallow: /` to every bot, so it isn't here.

The door scripts make one small, polite run each against the live sites. The speed benchmark never
touches Robinsons: `record.py` saved every mall directory once, one page a second, and `replay.py`
serves those pages from your laptop with the delay each one really took.

## Setup

Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install aiohttp requests beautifulsoup4 playwright
python -m playwright install chromium        # only for door 2
```

Optional, for the free-threaded row of the benchmark: a Python 3.14t interpreter with `requests` and
`beautifulsoup4` installed, at `.venv-ft/bin/python` or passed as `python bench.py --ft-python PATH`.

## On stage

The talk runs every demo from the notebook, in slide order. Before going on: open
`navigating_the_grey.ipynb` in Colab, run Part 0, add the `PROXIES` secret for
Part 3, then **Edit → Clear all outputs** so every cell runs fresh. Each slide's speaker notes name the
step to run (1.2, 2.1, …). Download a rehearsed copy with its outputs as the no-Wi-Fi fallback.

The scripts here do the same from a terminal:

```bash
python replay.py                     # terminal 1, leave running (http://127.0.0.1:8800)
python door1_robinsons.py            # terminal 2
python door2_megaworld.py
python door2_megaworld.py --headful  # the same page in a window the room can watch (needs a screen)
python door3_megaworld_api.py
python scale_1_sync.py               # start during "Where the Time Goes": about 33 s
python scale_3_asyncio.py            # the same 53 malls in about 2.5 s
```

Don't run `scale_4_processes.py` live on a Mac or Windows laptop. Those start every worker with
`spawn`, a fresh Python each, and 32 of them took 9.5 s on the 2-core test machine (fork: 2.5 s).
Since Python 3.14 the Linux default is `forkserver`, so the `if __name__ == "__main__":` guard is
needed on every platform.

No Wi-Fi? Add `--replay` to any door command. Door 1 then reads the same page from `replay.py`,
door 3 reads the API responses saved in `recordings/megaworld/`, and door 2 shows the saved shell and
says what the browser run found (a browser needs the live site).

## Slide ↔ file

| Slide | File |
|---|---|
| Today's Job | `robinsons_malls.json`, `malls.py` |
| Where Does the Data Live? | `robinsons_malls.json`, `malls.py` |
| Door 1 · Requests + BeautifulSoup | `door1_robinsons.py` |
| Door 2 · Playwright | `door2_megaworld.py` |
| Door 2 · Headful or Headless? | `door2_megaworld.py --headful`; `navigating_the_grey.ipynb`, step 1.3 |
| Door 3 · The Page's Own API | `door3_megaworld_api.py` |
| Where the Time Goes | `recordings/robinsons/timings.json` |
| Sync vs Async, Side by Side | `three_malls.py` (the three-mall bars), `scale_1_sync.py`, `scale_3_asyncio.py` |
| Threads vs Processes, Side by Side | `scale_2_threads.py`, `scale_4_processes.py`, `memory.py` (memory per worker) |
| All 53 Malls, Six Ways | `bench.py` → `results.json` (adds `scale_5_hybrid.py`) |
| They Set the Bar | `ramp.py` → `ramp.json` (a test server, never a real site) |
| Your IP Is a Signal | `navigating_the_grey.ipynb`, Part 3 |
| PengePassportPH, Polite by Construction | `navigating_the_grey.ipynb`, Part 4 (a bonus, not run on stage) |
| Everything, in a browser | `navigating_the_grey.ipynb` |

## The numbers on the slides

`python bench.py --runs 3` on a 2-core cloud VM, Python 3.13, 14 Oct 2026, median of 3 runs, against
the replay of 53 malls (8,554 stores; median page 511 ms of waiting and about 35 ms of parsing):

| Model | Time | vs the for loop |
|---|---:|---:|
| Sync, a for loop | 32.6 s | 1x |
| 32 threads | 2.9 s | 11x |
| asyncio, 32 at once | 2.5 s | 13x |
| 32 processes (fork) | 2.6 s | 13x |
| A process per core (2), asyncio inside | 2.0 s | 16x |
| 32 threads, Python 3.14t (no GIL) | 2.0 s | 16x |
| The slowest mall (Opus Mall) on its own | 1.95 s | the floor |

93% of the for loop's 32.6 s is waiting on the network. Your laptop will differ, especially for
processes (more cores, and `spawn` on macOS and Windows). Re-record from the network you present from
(`python record.py`, about two minutes), then run `python bench.py --runs 3` and update the slides if
the numbers move.

`python ramp.py` starts its own test server on port 8801 that can send only 20 pages a second, then holds
4, 8, … 40 requests a second for 6 seconds each (about 1.5 minutes). It never touches a real site:

| Sent/s | 4 | 8 | 12 | 16 | 20 | 24 | 28 | 32 | 36 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| Got/s | 4.0 | 8.0 | 12.0 | 16.0 | 19.6 | 19.7 | 19.8 | 19.8 | 17.7 | 12.3 |
| 429s | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 67 | 106 | 160 |

The plateau, about 20 pages a second, is the one we programmed. It's a ceiling, not a budget: a server
can stay below it and still be struggling, and many slow down or drop connections instead of sending 429.
Never ramp someone else's site to find it. Use their stated limit if they publish one; otherwise start
low, and back off on slow answers, errors and `Retry-After`.

`python three_malls.py` (with `replay.py` running) times Cybergate Davao, Tagum and GenSan one at a
time and all at once: about 1.4 s and 0.6 s. `python memory.py` measures what a worker costs: an idle
thread adds about 11 to 17 KB; a process worker has about 6 to 14 MB of its own (Linux only).

## Notes

- Megaworld's Contentstack keys in `door3_megaworld_api.py` are the public, read-only delivery tokens
  the site sends to every visitor's browser.
- `record.py` and `record_megaworld.py` identify themselves in the User-Agent and wait a second
  between requests. Keep it that way if you re-record.
