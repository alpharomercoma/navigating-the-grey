"""Door 2: Megaworld's mall page is an empty shell, and JavaScript fills it. A real browser runs it.

    python -m playwright install chromium            # once
    python -m doors.door2_megaworld
    python -m doors.door2_megaworld --headful    # the same, in a window you can watch (needs a screen)
    python -m doors.door2_megaworld --replay     # no Wi-Fi: the saved shell, and the browser run's result
"""
import os
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

URL = "https://www.megaworld-lifestylemalls.com/malls/uptown-mall"

if __name__ == "__main__":
    REPLAY = "--replay" in sys.argv
    HEADFUL = "--headful" in sys.argv
    t = time.perf_counter()
    if REPLAY:
        shell = (Path(__file__).resolve().parents[1] / "data/recordings/megaworld/uptown-mall.html").read_text()
    else:
        shell = requests.get(URL).text
    print(f"What requests sees: {len(shell.encode()) / 1000:.1f} KB, "
          f"{shell.count('store-item-name')} stores, in {time.perf_counter() - t:.1f} s")
    print('  <div id="root"></div>')
    print("  <noscript>You need to enable JavaScript to run this app.</noscript>\n")
    assert '<div id="root"></div>' in shell.replace("\n", "")

    if REPLAY:
        print("(replayed) A browser needs the live site. Rehearsal run, 14 Oct 2026:")
        print("What Playwright sees: 10 stores in about 12 s, after about 130 requests")
        sys.exit()

    # only needed behind a corporate or cloud proxy
    proxy = {"proxy": {"server": os.environ["HTTPS_PROXY"]}} if os.environ.get("HTTPS_PROXY") else {}

    seen = []
    t = time.perf_counter()
    # what the slide shows, line for line (plus the proxy, the request counter and --headful)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not HEADFUL, **proxy)   # headless unless --headful
        page = browser.new_page()
        page.on("request", lambda r: seen.append(r))
        page.goto(URL)                # Uptown Mall
        page.wait_for_selector(".store-item")
        cards = page.locator(".store-item-name")
        names = cards.all_inner_texts()  # after JS
        seconds = time.perf_counter() - t
        agent, webdriver = page.evaluate(
            "() => [navigator.userAgent.match(/(Headless)?Chrome/)[0], navigator.webdriver]")
        if HEADFUL:
            cards.first.scroll_into_view_if_needed()
            page.wait_for_timeout(3000)   # leave the window up long enough to see
        browser.close()

    print(f"What Playwright sees ({'headful' if HEADFUL else 'headless'}): {len(names)} stores in "
          f"{seconds:.1f} s, after {len(seen)} requests (browser start included)")
    print(" ", names[:5])
    print(f"What the page sees: {agent}, navigator.webdriver = {webdriver}")
