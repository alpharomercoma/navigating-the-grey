"""The 53 Robinsons malls that have a directory page, and where to fetch them."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MALLS = json.loads((HERE / "robinsons_malls.json").read_text())
SLUGS = [m["slug"] for m in MALLS]

LIVE = "https://robinsonsmalls.com/mall-info/"   # the real site: door 1, one page
URL = "http://127.0.0.1:8800/mall-info/"         # replay.py: every mall, on your laptop
