"""Scrape the public GitHub contribution calendar (no token) into data/contributions.json."""
import json
import re
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

USERNAME = "Malang27"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}      # cell id -> {date, level}
        self.tips = {}       # cell id -> tooltip text
        self._tip_for = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and "data-date" in a:
            self.cells[a["id"]] = {"date": a["data-date"], "level": int(a.get("data-level", 0))}
        elif tag == "tool-tip":
            self._tip_for = a.get("for")

    def handle_data(self, data):
        if self._tip_for:
            self.tips[self._tip_for] = self.tips.get(self._tip_for, "") + data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self._tip_for = None


def parse_count(text):
    m = re.match(r"\s*([\d,]+) contribution", text or "")
    return int(m.group(1).replace(",", "")) if m else 0


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    # today may not have activity yet; don't break the streak for it
    rev = days[::-1]
    if rev and rev[0]["count"] == 0:
        rev = rev[1:]
    for d in rev:
        if not d["count"]:
            break
        current += 1
    return current, longest


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "profile-readme-bot"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    p = CalendarParser()
    p.feed(html)

    days = sorted(
        ({"date": c["date"], "level": c["level"], "count": parse_count(p.tips.get(cid))}
         for cid, c in p.cells.items()),
        key=lambda d: d["date"],
    )
    if not days:
        raise SystemExit("no contribution cells found — GitHub markup may have changed")

    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "username": USERNAME,
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly": monthly,
        "days": days,
    }, indent=1), encoding="utf-8")
    print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions")


if __name__ == "__main__":
    main()
