"""Refresh src/data/github.json: the contribution calendar per year and star counts.

Needs a token, because the contribution calendar is only available through the
GraphQL API: set GITHUB_TOKEN, or be logged in with the gh CLI.

    python scripts/fetch-github.py
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LOGIN = "PalmaLuv"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "github.json"
PROFILE = ROOT / "content" / "profile.json"

CALENDAR = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""
REPO = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) { stargazerCount pushedAt description }
}
"""


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


# ---- no token: the public contributions page carries the same calendar ----
import re

WORDS = {"No": 0}


def scrape_year(year):
    url = f"https://github.com/users/{LOGIN}/contributions?from={year}-01-01&to={year}-12-31"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    ids = {cid: day for day, cid in re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?id="([^"]+)"', html)}
    days = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*(\d+|No)\s+contributions?", text)
        date = ids.get(cid)
        if m and date and date.startswith(str(year)):
            n = 0 if m.group(1) == "No" else int(m.group(1))
            if n:
                days[date] = n
    return days


def rest_repo(full):
    req = urllib.request.Request(f"https://api.github.com/repos/{full}", headers={"User-Agent": LOGIN, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return {"stars": d["stargazers_count"], "pushed": d["pushed_at"][:10]}


def rest_created():
    req = urllib.request.Request(f"https://api.github.com/users/{LOGIN}", headers={"User-Agent": LOGIN})
    with urllib.request.urlopen(req, timeout=30) as r:
        return int(json.load(r)["created_at"][:4])


def gql(tok, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {tok}", "Content-Type": "application/json", "User-Agent": LOGIN},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "errors" in out:
        raise SystemExit(out["errors"])
    return out["data"]


def main():
    tok = token()
    this_year = datetime.now(timezone.utc).year
    calendar = {}
    projects = json.loads(PROFILE.read_text(encoding="utf-8"))["projects"]
    stars = {}

    if tok:
        first = gql(tok, CALENDAR, {"login": LOGIN, "from": f"{this_year}-01-01T00:00:00Z", "to": f"{this_year}-12-31T23:59:59Z"})
        created = int(first["user"]["createdAt"][:4])
        years = list(range(created, this_year + 1))
        for y in years:
            d = first if y == this_year else gql(tok, CALENDAR, {"login": LOGIN, "from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"})
            days = {}
            for w in d["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
                for day in w["contributionDays"]:
                    if day["contributionCount"] and day["date"].startswith(str(y)):
                        days[day["date"]] = day["contributionCount"]
            calendar[str(y)] = days
        for p in projects:
            owner, name = p["repo"].split("/")
            r = gql(tok, REPO, {"owner": owner, "name": name})["repository"]
            stars[p["repo"]] = {"stars": r["stargazerCount"], "pushed": r["pushedAt"][:10]}
    else:
        print("no token, reading the public contributions page instead")
        created = rest_created()
        years = list(range(created, this_year + 1))
        for y in years:
            calendar[str(y)] = scrape_year(y)
        for p in projects:
            stars[p["repo"]] = rest_repo(p["repo"])

    data = {
        "login": LOGIN,
        "fetched": datetime.now(timezone.utc).date().isoformat(),
        "years": [y for y in years if calendar[str(y)]] or years[-1:],
        "calendar": {y: v for y, v in calendar.items() if v},
        "repos": stars,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    total = sum(sum(v.values()) for v in calendar.values())
    print(f"wrote {OUT}: {len(data['years'])} years, {total} contributions, {len(stars)} repos")
    for y in data["years"]:
        print(f"  {y}: {len(calendar[str(y)])} days, {sum(calendar[str(y)].values())} contributions")


if __name__ == "__main__":
    main()
