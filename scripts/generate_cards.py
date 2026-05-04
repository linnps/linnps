"""
Generate SVG profile cards from public GitHub data.

Run locally:
    GH_TOKEN=$(gh auth token) GH_USER=linnps python scripts/generate_cards.py

Run in GitHub Actions:
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GH_USER: linnps

Outputs:
    assets/cards/stats.svg
    assets/cards/top-langs.svg
    assets/cards/streak.svg

Palette is the same one used across the ML portfolio:
    background  #FFFFFF        title   #3B6EA8 (blue)
    border      #E5E5E5        accent  #C04040 (red)
    text        #333333        muted   #7A7A7A (gray)
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from html import escape
from pathlib import Path

# ---------------------------------------------------------------------- env
USER = os.environ.get("GH_USER", "linnps")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    sys.exit("error: set GH_TOKEN or GITHUB_TOKEN")

OUT = Path("assets/cards")
OUT.mkdir(parents=True, exist_ok=True)

# Portfolio palette
BG       = "#FFFFFF"
GRID     = "#E5E5E5"
LIGHT    = "#CCCCCC"
TEXT     = "#333333"
TITLE    = "#3B6EA8"   # blue
ACCENT   = "#C04040"   # red
MUTED    = "#7A7A7A"   # gray


# -------------------------------------------------------------- GraphQL
QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    followers { totalCount }
    repositories(first: 100, isFork: false, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        name
        isFork
        stargazerCount
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch() -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": f"profile-cards-generator/{USER}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.loads(r.read())
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]["user"]


# -------------------------------------------------------------- aggregate
def aggregate(user: dict) -> dict:
    repos = user["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)

    lang_size: dict[str, int] = defaultdict(int)
    lang_color: dict[str, str] = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            lang_size[n] += e["size"]
            lang_color[n] = e["node"]["color"] or "#888888"

    total_size = sum(lang_size.values()) or 1
    langs = [
        (name, lang_color[name], 100.0 * size / total_size)
        for name, size in sorted(lang_size.items(), key=lambda x: -x[1])
    ]

    # Streaks from the contribution calendar (last ~365 days of public data)
    days: list[tuple[str, int]] = []
    for w in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    days.sort(key=lambda x: x[0])

    longest = run = 0
    for _, c in days:
        if c > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    # Current streak: walk backwards from latest day. If today has 0
    # contributions we still allow yesterday's streak to count (mirrors
    # the conventional Github-streak semantics).
    current = 0
    for _, c in reversed(days):
        if c > 0:
            current += 1
        elif current == 0:
            continue   # leading zeros (e.g., today not yet committed)
        else:
            break

    cc = user["contributionsCollection"]
    return {
        "user": user["login"],
        "stars": stars,
        "repos": user["repositories"]["totalCount"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "contributed_repos": cc["totalRepositoriesWithContributedCommits"],
        "followers": user["followers"]["totalCount"],
        "languages": langs,
        "total_contributions": cc["contributionCalendar"]["totalContributions"],
        "current_streak": current,
        "longest_streak": longest,
    }


# -------------------------------------------------------------- SVG render
def card(width: int, height: int, body: str, title: str | None = None,
         subtitle: str | None = None) -> str:
    title_xml = ""
    if title:
        title_xml = (
            f'<text x="{width/2}" y="32" fill="{TITLE}" font-size="16" '
            f'font-weight="700" text-anchor="middle" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">'
            f'{escape(title)}</text>'
            f'<line x1="20" y1="46" x2="{width-20}" y2="46" '
            f'stroke="{LIGHT}" stroke-width="0.6"/>'
        )
    sub_xml = ""
    if subtitle:
        sub_xml = (
            f'<text x="{width/2}" y="{height-10}" fill="{MUTED}" font-size="10" '
            f'text-anchor="middle" font-family="sans-serif">'
            f'{escape(subtitle)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,sans-serif">'
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" '
        f'rx="8" fill="{BG}" stroke="{GRID}" stroke-width="1"/>'
        f'{title_xml}{body}{sub_xml}</svg>'
    )


def render_stats(s: dict) -> str:
    rows = [
        ("Total stars",        s["stars"]),
        ("Public repos",       s["repos"]),
        ("Commits (last yr)",  s["commits"]),
        ("Pull requests",      s["prs"]),
        ("Issues opened",      s["issues"]),
        ("Followers",          s["followers"]),
    ]
    parts: list[str] = []
    y = 70
    for label, value in rows:
        parts.append(
            f'<text x="22" y="{y}" fill="{TEXT}" font-size="13">{escape(label)}</text>'
            f'<text x="318" y="{y}" fill="{ACCENT}" font-size="14" font-weight="700" '
            f'text-anchor="end">{value:,}</text>'
        )
        y += 22
    today = datetime.date.today().isoformat()
    return card(340, 210, "".join(parts),
                title=f"{s['user']} — GitHub Stats",
                subtitle=f"updated {today}")


def render_languages(s: dict) -> str:
    langs = s["languages"][:6]
    parts: list[str] = []
    bar_x, bar_max = 120, 170
    y = 65
    for name, color, pct in langs:
        bw = max(2, int(bar_max * pct / 100))
        parts.append(
            f'<text x="22" y="{y+10}" fill="{TEXT}" font-size="12">{escape(name)}</text>'
            f'<rect x="{bar_x}" y="{y}" width="{bar_max}" height="10" '
            f'rx="3" fill="{LIGHT}" opacity="0.55"/>'
            f'<rect x="{bar_x}" y="{y}" width="{bw}" height="10" rx="3" fill="{color}"/>'
            f'<text x="318" y="{y+10}" fill="{MUTED}" font-size="11" '
            f'text-anchor="end">{pct:.1f}%</text>'
        )
        y += 22
    if not langs:
        parts.append(f'<text x="170" y="100" fill="{MUTED}" font-size="13" '
                     f'text-anchor="middle">No language data available.</text>')
    today = datetime.date.today().isoformat()
    return card(340, 210, "".join(parts),
                title="Most Used Languages",
                subtitle=f"by bytes across public non-fork repos · {today}")


def render_streak(s: dict) -> str:
    sections = [
        ("Total Contributions", s["total_contributions"], "in the last year"),
        ("Current Streak",      s["current_streak"],      "day(s)"),
        ("Longest Streak",      s["longest_streak"],      "day(s)"),
    ]
    width = 700
    section_w = (width - 40) / 3
    parts: list[str] = []
    for i, (label, value, sub) in enumerate(sections):
        cx = 20 + section_w * (i + 0.5)
        parts.append(
            f'<text x="{cx}" y="100" fill="{ACCENT}" font-size="38" font-weight="700" '
            f'text-anchor="middle">{value:,}</text>'
            f'<text x="{cx}" y="135" fill="{TEXT}" font-size="13" font-weight="700" '
            f'text-anchor="middle">{escape(label)}</text>'
            f'<text x="{cx}" y="155" fill="{MUTED}" font-size="11" '
            f'text-anchor="middle">{escape(sub)}</text>'
        )
        if i < 2:
            x = 20 + section_w * (i + 1)
            parts.append(
                f'<line x1="{x}" y1="65" x2="{x}" y2="160" '
                f'stroke="{LIGHT}" stroke-width="0.6"/>'
            )
    today = datetime.date.today().isoformat()
    return card(width, 200, "".join(parts),
                title=f"Activity — {s['user']}",
                subtitle=f"updated {today}")


# ----------------------------------------------------------------- main
def main() -> None:
    print(f"fetching public stats for {USER}…")
    user = fetch()
    s = aggregate(user)

    print(f"  stars={s['stars']}  repos={s['repos']}  "
          f"commits(yr)={s['commits']}  prs={s['prs']}  "
          f"contribs={s['total_contributions']}  "
          f"streak now/longest={s['current_streak']}/{s['longest_streak']}")
    print(f"  languages: {[(n, f'{p:.1f}%') for n, _, p in s['languages'][:5]]}")

    (OUT / "stats.svg").write_text(render_stats(s))
    (OUT / "top-langs.svg").write_text(render_languages(s))
    (OUT / "streak.svg").write_text(render_streak(s))
    print(f"wrote 3 SVGs to {OUT.resolve()}")


if __name__ == "__main__":
    main()
