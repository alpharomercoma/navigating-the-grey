"""A stand-in for passport.gov.ph, so Part 4 can run without touching the real site.

Same paths and the same quirks: /appointment hands out a token plus a matching cookie, and the
token-protected endpoints answer an empty 200 when they're missing. The answers are pages recorded
from passport.gov.ph for PengePassportPH's test suite (Antipolo, site 486, late Sep to early Oct 2026).

    python -m replay.passport_standin    # http://127.0.0.1:8802
"""
import argparse
import itertools
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

SAVED = Path(__file__).resolve().parents[1] / "data" / "recordings" / "passport"
BOOTSTRAP = (SAVED / "bootstrap-appointment.html").read_text(encoding="utf-8")
JSON = {"/countries": "countries-region1.json", "/sites": "sites-region1-country1.json",
        "/appointment/timeslot/available": "availability-site486.json"}
HOURS = (SAVED / "timeslot-2026-10-05-site486.html").read_text(encoding="utf-8")

issued, counter, lock = set(), itertools.count(1), threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def answer(self):
        path = urlsplit(self.path).path
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        token = self.headers.get("__RequestVerificationToken", "")
        has_token = token in issued and f"__RequestVerificationToken=cookie-{token}" in self.headers.get("Cookie", "")
        cookie = None
        if path == "/health":
            kind, body = "text/plain", "ok"
        elif path == "/appointment":
            with lock:
                token = f"T{next(counter)}"
                issued.add(token)
            kind, body = "text/html", BOOTSTRAP.replace("FIXTURE-FORM-TOKEN", token)
            cookie = f"__RequestVerificationToken=cookie-{token}; path=/; HttpOnly"
        elif path in ("/countries", "/sites"):
            kind, body = "application/json", (SAVED / JSON[path]).read_text(encoding="utf-8")
        elif path == "/appointment/timeslot/available":   # the site's quirk: no token, empty 200
            kind, body = "application/json", (SAVED / JSON[path]).read_text(encoding="utf-8") if has_token else ""
        elif path == "/appointment/timeslot":
            kind, body = "text/html", HOURS if has_token else ""
        else:
            self.send_error(404)
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", f"{kind}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = answer

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8802)
    ThreadingHTTPServer(("127.0.0.1", ap.parse_args().port), Handler).serve_forever()
