"""Refresh src/data/leetcode.json from LeetCode's GraphQL API.

LeetCode does not send CORS headers, so the page cannot ask it directly;
run this script and commit the JSON instead.

    python scripts/fetch-leetcode.py
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "mrkyt875"
OUT = Path(__file__).resolve().parent.parent / "src" / "data" / "leetcode.json"

QUERY = """
query($u: String!, $y: Int) {
  matchedUser(username: $u) {
    userCalendar(year: $y) { activeYears streak totalActiveDays submissionCalendar }
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    languageProblemCount { languageName problemsSolved }
  }
}
"""


def gql(variables):
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/u/{USERNAME}/",
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["matchedUser"]


def main():
    first = gql({"u": USERNAME})
    years = sorted(first["userCalendar"]["activeYears"])
    calendars = {}
    for y in years:
        cal = gql({"u": USERNAME, "y": y})["userCalendar"]
        days = {}
        for ts, n in json.loads(cal["submissionCalendar"]).items():
            day = datetime.fromtimestamp(int(ts), timezone.utc).date().isoformat()
            days[day] = days.get(day, 0) + n
        calendars[str(y)] = days

    data = {
        "username": USERNAME,
        "fetched": datetime.now(timezone.utc).date().isoformat(),
        "solved": {d["difficulty"].lower(): d["count"] for d in first["submitStatsGlobal"]["acSubmissionNum"]},
        "languages": {l["languageName"]: l["problemsSolved"] for l in first["languageProblemCount"]},
        "years": years,
        "calendar": calendars,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    total_days = sum(len(v) for v in calendars.values())
    total_subs = sum(sum(v.values()) for v in calendars.values())
    print(f"wrote {OUT}: {len(years)} years, {total_days} active days, {total_subs} submissions")
    for y in years:
        print(f"  {y}: {len(calendars[str(y)])} days, {sum(calendars[str(y)].values())} submissions")


if __name__ == "__main__":
    main()
