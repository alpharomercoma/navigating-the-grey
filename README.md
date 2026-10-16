# Navigating the Grey: talk code

The demos and benchmarks from the PyCon Davao 2026 talk
*Navigating the Grey: Building Resilient Python Scrapers That Survive at Scale*.

**No setup? Run every demo in your browser:**
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alpharomercoma/navigating-the-grey/blob/main/navigating_the_grey.ipynb)
It's the talk's live demos, step by step: the three doors; 53 malls with a for loop, asyncio, threads,
processes and both, on a scoreboard next to the slides' numbers; SM direct and through your own proxies.
A bonus part, not run on stage, makes the requests inside PengePassportPH by hand before the package
makes them. The notebook's first cell clones this repo, recorded pages included, so the speed demos never
touch Robinsons, and the passport part runs against a local stand-in unless you tick LIVE.

Also from the talk:

- PengePassportPH: [alphaexperiments.com/p3h](https://alphaexperiments.com/p3h) ·
  [github.com/alpharomercoma/penge-passport-ph](https://github.com/alpharomercoma/penge-passport-ph)
- Philippine Mall Explorer: [alpharomercoma.github.io/philippine-mall-explorer](https://alpharomercoma.github.io/philippine-mall-explorer) ·
  [github.com/alpharomercoma/philippine-mall-explorer](https://github.com/alpharomercoma/philippine-mall-explorer)

## What's where

```
navigating_the_grey.ipynb    every demo, in Colab (the slides' QR code opens this file)
requirements.txt

doors/                       Part 1 · Where the data lives: one mall, three doors
  door1_robinsons.py           a static page, the stores in the HTML: requests + BeautifulSoup
  door2_megaworld.py           a dynamic page, empty until JavaScript runs: Playwright, headless or --headful
  door3_megaworld_api.py       the JSON the page fetches: requests .json()

scale/                       Part 2 · Being at scale: 53 malls, six ways
  step1_sync.py                a for loop, one mall at a time
  step2_threads.py             32 threads
  step3_asyncio.py             asyncio, 32 at once
  step4_processes.py           32 processes
  step5_hybrid.py              a process per core, asyncio inside
  three_malls.py               the three-mall timelines on "Sync vs Async"
  memory.py                    what a thread and a process cost
  bench.py                     all of the above, timed → results.json

limits/                      Part 3 · They set the bar
  ramp.py                      raise the rate on a test server and watch it push back → ramp.json

replay/                      record the real site once, replay it on your machine
  record_robinsons.py          saves the 53 Robinsons pages, one a second, with how long each took
  record_megaworld.py          saves Uptown Mall's page and API answers (the doors' no-Wi-Fi fallback)
  server.py                    serves the saved pages with the same delays: what Part 2 and 3 hit
  passport_standin.py          answers like passport.gov.ph from saved pages: the notebook's Part 4

common/                      shared: the mall list (malls.py), the timer (timing.py), the notebook's helpers (notebook.py)
data/                        robinsons_malls.json and the recordings: Robinsons, Megaworld, the passport site
```

Every script runs from the repo's top folder as a module, so the folders can import each other:
`python -m scale.step1_sync`, not `python scale/step1_sync.py`.

Two real Philippine mall sites, three ways to read them:

| Door | Site | What comes back | Script |
|---|---|---|---|
| 1 | robinsonsmalls.com/mall-info/robinsons-cybergate-davao | A static page: the stores are in the HTML | `doors/door1_robinsons.py` |
| 2 | megaworld-lifestylemalls.com/malls/uptown-mall | A dynamic page: empty until JavaScript fills it | `doors/door2_megaworld.py` |
| 3 | cdn.contentstack.io/…/tenant/entries | The JSON the page fetches | `doors/door3_megaworld_api.py` |

Both sites allow bots in robots.txt. Ayala's says `Disallow: /` to every bot, so it isn't here.

The doors make one small, polite run each against the live sites. The speed benchmark never touches
Robinsons: `replay/record_robinsons.py` saved every mall directory once, one page a second, and
`replay/server.py` serves those pages from your machine with the delay each one really took.

## Setup

Python 3.10 or newer.

```bash
git clone https://github.com/alpharomercoma/navigating-the-grey && cd navigating-the-grey
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium        # only for door 2
```

Optional, for the free-threaded row of the benchmark: a Python 3.14t interpreter with `requests` and
`beautifulsoup4` installed, at `.venv-ft/bin/python` or passed as `python -m scale.bench --ft-python PATH`.

## Run it

The talk runs every demo from the notebook, in slide order; each slide's speaker notes name the step
(1.2, 2.1, …). The scripts do the same from a terminal:

```bash
python -m replay.server                      # terminal 1, leave running (http://127.0.0.1:8800)

python -m doors.door1_robinsons              # terminal 2
python -m doors.door2_megaworld
python -m doors.door2_megaworld --headful    # the same page in a window you can watch (needs a screen)
python -m doors.door3_megaworld_api

python -m scale.step1_sync                   # about 33 s: start it during "Where the Time Goes"
python -m scale.step3_asyncio                # the same 53 malls in about 2.5 s
python -m scale.bench --runs 3               # all six, median of 3, as on the slides
python -m limits.ramp                        # starts its own test server; about 1.5 min
```

No Wi-Fi? Add `--replay` to any door. Door 1 then reads the same page from the replay server, door 3
reads the API answers saved in `data/recordings/megaworld/`, and door 2 shows the saved shell and says
what the browser run found (a browser needs the live site).

Don't run `scale.step4_processes` live on a Mac or Windows laptop. Those start every worker with
`spawn`, a fresh Python each, and 32 of them took 9.5 s on the 2-core test machine (fork: 2.5 s).
Since Python 3.14 the Linux default is `forkserver`, so the `if __name__ == "__main__":` guard is
needed on every platform.

## Slide ↔ file

| Slide | File |
|---|---|
| Today's Job, Where Does the Data Live? | `data/robinsons_malls.json`, `common/malls.py` |
| Door 1 · Finding the Selector, Door 1 · Requests + BeautifulSoup | `doors/door1_robinsons.py` |
| Door 2 · Uptown Mall in a Browser, Door 2 · Playwright | `doors/door2_megaworld.py` |
| Door 2 · Headful, Door 2 · Headless | `doors/door2_megaworld.py` with and without `--headful`; the notebook, step 1.3 |
| Door 3 · Find the Request, Door 3 · The Page's Own API | `doors/door3_megaworld_api.py` |
| Where the Time Goes | `data/recordings/robinsons/timings.json` |
| Sync vs Async, Side by Side | `scale/three_malls.py`, `scale/step1_sync.py`, `scale/step3_asyncio.py` |
| Threads vs Processes, Side by Side | `scale/step2_threads.py`, `scale/step4_processes.py`, `scale/memory.py` |
| All 53 Malls, Six Ways | `scale/bench.py` → `scale/results.json` (adds `scale/step5_hybrid.py`) |
| They Set the Bar | `limits/ramp.py` → `limits/ramp.json` (a test server, never a real site) |
| Your IP Is a Signal | the notebook, Part 3 |
| PengePassportPH, Polite by Construction | the notebook, Part 4 (a bonus, not run on stage) |

## The numbers on the slides

`python -m scale.bench --runs 3` on a 2-core cloud VM, Python 3.13, 14 Oct 2026, median of 3 runs,
against the replay of 53 malls (8,554 stores; median page 511 ms of waiting and about 35 ms of parsing):

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
(`python -m replay.record_robinsons`, about two minutes), then run `python -m scale.bench --runs 3` and
update the slides if the numbers move.

`python -m limits.ramp` starts its own test server on port 8801 that can send only 20 pages a second,
then holds 4, 8, … 40 requests a second for 6 seconds each. It never touches a real site:

| Sent/s | 4 | 8 | 12 | 16 | 20 | 24 | 28 | 32 | 36 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| Got/s | 4.0 | 8.0 | 12.0 | 16.0 | 19.6 | 19.7 | 19.8 | 19.8 | 17.7 | 12.3 |
| 429s | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 67 | 106 | 160 |

The plateau, about 20 pages a second, is the one we programmed. It's a ceiling, not a budget: a server
can stay below it and still be struggling, and many slow down or drop connections instead of sending 429.
Never ramp someone else's site to find it. Use their stated limit if they publish one; otherwise start
low, and back off on slow answers, errors and `Retry-After`.

`python -m scale.three_malls` (with the replay server running) times Cybergate Davao, Tagum and GenSan
one at a time and all at once: about 1.4 s and 0.6 s. `python -m scale.memory` measures what a worker
costs: an idle thread adds about 11 to 17 KB; a process worker has about 6 to 14 MB of its own (Linux only).

## Notes

- Megaworld's Contentstack keys in `doors/door3_megaworld_api.py` are the public, read-only delivery
  tokens the site sends to every visitor's browser.
- The recorders in `replay/` identify themselves in the User-Agent and wait a second between requests.
  Keep it that way if you re-record.
- The slides' door 2 recordings and the door 3 DevTools crop are on the
  [`slide-assets`](https://github.com/alpharomercoma/navigating-the-grey/tree/slide-assets) branch, with the
  script that recorded them.
