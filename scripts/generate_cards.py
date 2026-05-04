"""
Generate SVG profile cards from public GitHub data.

Run locally:
    GH_TOKEN=$(gh auth token) GH_USER=linnps python scripts/generate_cards.py

Run in GitHub Actions:
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GH_USER: linnps

Outputs (all under assets/cards/):
    stats.svg                340 × 195 — six headline counters
    top-langs.svg            340 × 195 — top languages with horizontal bars
    streak.svg               340 × 195 — total / current / longest contributions
    weekday-distribution.svg 340 × 195 — bar histogram of contributions by weekday
    cumulative-curve.svg     340 × 195 — running-total curve over the year
    weekly-trend.svg         340 × 195 — area chart of last 26 weeks
    activity-graph.svg       780 × 150 — full-year contribution heatmap
    top-repos.svg            700 × ... — top-starred repos with metadata
    repo-tiles.svg           700 × 180 — mosaic of every repo by primary language

Palette (same one used across the ML portfolio):
    background  #FFFFFF        title   #3B6EA8 (blue)
    border      #E5E5E5        accent  #C04040 (red)
    text        #333333        muted   #7A7A7A (gray)
"""

from __future__ import annotations

import datetime
import json
import math
import os
import sys
import urllib.request
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

# Heatmap intensity ladder (light → blue → red for hot days)
HEAT = ["#EEEEEE", "#D8E0EC", "#9EB7D6", "#3B6EA8", "#C04040"]


# -------------------------------------------------------------- GraphQL
QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    createdAt
    followers { totalCount }
    repositories(first: 100, isFork: false, privacy: PUBLIC,
                 ownerAffiliations: OWNER,
                 orderBy: { field: STARGAZERS, direction: DESC }) {
      totalCount
      nodes {
        name
        description
        url
        stargazerCount
        forkCount
        updatedAt
        createdAt
        primaryLanguage { name color }
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
            weekday
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

    days: list[tuple[str, int, int]] = []
    for w in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            days.append((d["date"], d["contributionCount"], d["weekday"]))
    days.sort(key=lambda x: x[0])

    longest = run = 0
    for _, c, _ in days:
        if c > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    current = 0
    for _, c, _ in reversed(days):
        if c > 0:
            current += 1
        elif current == 0:
            continue
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
        "days": days,
        "repos_meta": repos,
        "created_at": user["createdAt"],
    }


# -------------------------------------------------------------- SVG helpers
def card(width: int, height: int, body: str, title: str | None = None,
         subtitle: str | None = None) -> str:
    title_xml = ""
    if title:
        title_xml = (
            f'<text x="{width/2}" y="26" fill="{TITLE}" font-size="13" '
            f'font-weight="700" text-anchor="middle">'
            f'{escape(title)}</text>'
            f'<line x1="16" y1="38" x2="{width-16}" y2="38" '
            f'stroke="{LIGHT}" stroke-width="0.6"/>'
        )
    sub_xml = ""
    if subtitle:
        sub_xml = (
            f'<text x="{width/2}" y="{height-8}" fill="{MUTED}" font-size="9" '
            f'text-anchor="middle">{escape(subtitle)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">'
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" '
        f'rx="8" fill="{BG}" stroke="{GRID}" stroke-width="1"/>'
        f'{title_xml}{body}{sub_xml}</svg>'
    )


def heat_color(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return HEAT[0]
    if count >= max_count * 0.85:
        return HEAT[4]
    ratio = count / max_count
    idx = 1 + min(3, int(ratio / 0.21))
    return HEAT[idx]


# -------------------------------------------------------------- card 1: stats (340x195)
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
    y = 60
    for label, value in rows:
        parts.append(
            f'<text x="20" y="{y}" fill="{TEXT}" font-size="11">{escape(label)}</text>'
            f'<text x="320" y="{y}" fill="{ACCENT}" font-size="13" font-weight="700" '
            f'text-anchor="end">{value:,}</text>'
        )
        y += 19
    today = datetime.date.today().isoformat()
    return card(340, 195, "".join(parts),
                title=f"{s['user']} — GitHub Stats",
                subtitle=f"updated {today}")


# -------------------------------------------------------------- card 2: top-langs (340x195)
def render_languages(s: dict) -> str:
    langs = s["languages"][:6]
    parts: list[str] = []
    bar_x, bar_max = 110, 175
    y = 56
    for name, color, pct in langs:
        bw = max(2, int(bar_max * pct / 100))
        parts.append(
            f'<text x="20" y="{y+8}" fill="{TEXT}" font-size="11">{escape(name)}</text>'
            f'<rect x="{bar_x}" y="{y}" width="{bar_max}" height="9" '
            f'rx="2.5" fill="{LIGHT}" opacity="0.55"/>'
            f'<rect x="{bar_x}" y="{y}" width="{bw}" height="9" rx="2.5" fill="{color}"/>'
            f'<text x="320" y="{y+8}" fill="{MUTED}" font-size="10" '
            f'text-anchor="end">{pct:.1f}%</text>'
        )
        y += 19
    if not langs:
        parts.append(f'<text x="170" y="100" fill="{MUTED}" font-size="11" '
                     f'text-anchor="middle">No language data available.</text>')
    today = datetime.date.today().isoformat()
    return card(340, 195, "".join(parts),
                title="Most Used Languages",
                subtitle=f"by bytes · {today}")


# -------------------------------------------------------------- card 3: streak (340x195)
def render_streak(s: dict) -> str:
    rows = [
        (s["total_contributions"], "Total Contributions", "in the last year"),
        (s["current_streak"],      "Current Streak",      "day(s)"),
        (s["longest_streak"],      "Longest Streak",      "day(s) — all-time peak"),
    ]
    parts: list[str] = []
    y = 60
    for value, label, sub in rows:
        parts.append(
            f'<text x="100" y="{y}" fill="{ACCENT}" font-size="26" font-weight="700" '
            f'text-anchor="end">{value:,}</text>'
            f'<text x="115" y="{y-7}" fill="{TEXT}" font-size="12" font-weight="700">'
            f'{escape(label)}</text>'
            f'<text x="115" y="{y+7}" fill="{MUTED}" font-size="10">{escape(sub)}</text>'
        )
        y += 42
    today = datetime.date.today().isoformat()
    return card(340, 195, "".join(parts),
                title=f"Activity — {s['user']}",
                subtitle=f"updated {today}")


# -------------------------------------------------------------- card 4: weekday histogram (340x195)
def render_weekday_distribution(s: dict) -> str:
    """
    Bar histogram of total contributions by day-of-week.
    GitHub uses weekday 0 = Sunday … 6 = Saturday.
    """
    width, height = 340, 195
    by_wd = [0] * 7
    for _, count, wd in s["days"]:
        by_wd[wd] += count
    labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    max_v = max(by_wd) or 1

    plot_x = 38
    plot_y = 56
    plot_w = width - plot_x - 14
    plot_h = height - plot_y - 38

    bar_slot = plot_w / 7
    bar_w = bar_slot * 0.62
    parts: list[str] = []

    # Y-axis gridlines (4 ticks).
    for j in range(5):
        y = plot_y + plot_h * (1 - j / 4)
        v = int(round(max_v * j / 4))
        parts.append(
            f'<line x1="{plot_x}" y1="{y}" x2="{plot_x + plot_w}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="0.5"/>'
            f'<text x="{plot_x - 4}" y="{y + 3}" fill="{MUTED}" font-size="8" '
            f'text-anchor="end">{v}</text>'
        )

    max_idx = by_wd.index(max(by_wd))
    for i, c in enumerate(by_wd):
        cx = plot_x + (i + 0.5) * bar_slot
        bx = cx - bar_w / 2
        h = (c / max_v) * plot_h
        by = plot_y + plot_h - h
        color = ACCENT if i == max_idx and c > 0 else TITLE
        parts.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" '
            f'height="{h:.1f}" rx="2" fill="{color}">'
            f'<title>{labels[i]}: {c} contribution(s)</title></rect>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{plot_y + plot_h + 12}" '
            f'fill="{MUTED}" font-size="9" text-anchor="middle">{labels[i]}</text>'
        )
        if c > 0:
            parts.append(
                f'<text x="{cx:.1f}" y="{by - 3:.1f}" fill="{TEXT}" font-size="9" '
                f'text-anchor="middle">{c}</text>'
            )

    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title="Weekday rhythm (last 12 months)",
                subtitle=f"red bar = busiest weekday · {today}")


# -------------------------------------------------------------- card 5: cumulative curve (340x195)
def render_cumulative_curve(s: dict) -> str:
    """Running-total curve of contributions across the past year."""
    width, height = 340, 195
    days = s["days"]
    if not days:
        return card(width, height, "", title="Cumulative contributions")

    # Running sum.
    running: list[tuple[str, int]] = []
    total = 0
    for date, count, _ in days:
        total += count
        running.append((date, total))

    final = total
    if final == 0:
        return card(width, height,
                    f'<text x="170" y="100" fill="{MUTED}" font-size="11" '
                    f'text-anchor="middle">No contributions yet.</text>',
                    title="Cumulative contributions")

    plot_x = 38
    plot_y = 54
    plot_w = width - plot_x - 18
    plot_h = height - plot_y - 38

    n = len(running)
    points: list[tuple[float, float]] = []
    for i, (_, v) in enumerate(running):
        x = plot_x + (i / max(1, n - 1)) * plot_w
        y = plot_y + plot_h - (v / final) * plot_h
        points.append((x, y))

    parts: list[str] = []
    # gridlines
    for j in range(5):
        y = plot_y + plot_h * (1 - j / 4)
        v = int(round(final * j / 4))
        parts.append(
            f'<line x1="{plot_x}" y1="{y}" x2="{plot_x + plot_w}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="0.5"/>'
            f'<text x="{plot_x - 4}" y="{y + 3}" fill="{MUTED}" font-size="8" '
            f'text-anchor="end">{v}</text>'
        )

    # area
    area = (
        f"M {plot_x} {plot_y + plot_h:.1f} "
        + " ".join(f"L {x:.1f} {y:.1f}" for x, y in points)
        + f" L {plot_x + plot_w:.1f} {plot_y + plot_h:.1f} Z"
    )
    parts.append(
        f'<path d="{area}" fill="{TITLE}" fill-opacity="0.18" stroke="none"/>'
    )

    # curve
    curve = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    parts.append(
        f'<path d="{curve}" fill="none" stroke="{TITLE}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # endpoint marker + total
    fx, fy = points[-1]
    parts.append(
        f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3.5" fill="{ACCENT}" '
        f'stroke="{BG}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{fx - 8:.1f}" y="{fy - 5:.1f}" fill="{ACCENT}" font-size="11" '
        f'font-weight="700" text-anchor="end">{final}</text>'
    )

    # x-axis labels (start, mid, end month).
    for i in (0, n // 2, n - 1):
        d = datetime.date.fromisoformat(running[i][0])
        x = plot_x + (i / max(1, n - 1)) * plot_w
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        parts.append(
            f'<text x="{x:.1f}" y="{plot_y + plot_h + 12}" fill="{MUTED}" '
            f'font-size="9" text-anchor="{anchor}">{d.strftime("%b %Y")}</text>'
        )

    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title="Cumulative contributions",
                subtitle=f"running total · ends at {final} on {today}")


# -------------------------------------------------------------- card 6: weekly-trend (340x195)
def render_weekly_trend(s: dict) -> str:
    width, height = 340, 195
    days = s["days"]
    if not days:
        return card(width, height, "", title="Weekly contribution trend")

    n_weeks = 26
    last_n = days[-n_weeks * 7:]
    weekly_totals: list[tuple[str, int]] = []
    for i in range(0, len(last_n), 7):
        wk = last_n[i:i + 7]
        if not wk:
            continue
        weekly_totals.append((wk[0][0], sum(c for _, c, _ in wk)))

    if not weekly_totals:
        return card(width, height, "", title="Weekly contribution trend")

    plot_x = 36
    plot_y = 56
    plot_w = width - plot_x - 14
    plot_h = height - plot_y - 38

    max_y = max((c for _, c in weekly_totals), default=0) or 1
    n = len(weekly_totals)
    step = plot_w / max(1, n - 1) if n > 1 else 0

    points: list[tuple[float, float]] = []
    for i, (_, c) in enumerate(weekly_totals):
        x = plot_x + i * step
        y = plot_y + plot_h - (c / max_y) * plot_h
        points.append((x, y))

    parts: list[str] = []
    for j in range(5):
        y = plot_y + plot_h * (1 - j / 4)
        v = int(round(max_y * j / 4))
        parts.append(
            f'<line x1="{plot_x}" y1="{y}" x2="{plot_x + plot_w}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="0.5"/>'
            f'<text x="{plot_x - 4}" y="{y + 3}" fill="{MUTED}" font-size="8" '
            f'text-anchor="end">{v}</text>'
        )

    for i in range(0, n, max(1, n // 5)):
        d = datetime.date.fromisoformat(weekly_totals[i][0])
        x = plot_x + i * step
        parts.append(
            f'<text x="{x:.1f}" y="{plot_y + plot_h + 12}" fill="{MUTED}" '
            f'font-size="8" text-anchor="middle">{d.strftime("%b %d")}</text>'
        )

    area = (
        f'M {plot_x} {plot_y + plot_h:.1f} '
        + " ".join(f"L {x:.1f} {y:.1f}" for x, y in points)
        + f' L {plot_x + (n - 1) * step:.1f} {plot_y + plot_h:.1f} Z'
    )
    parts.append(
        f'<path d="{area}" fill="{TITLE}" fill-opacity="0.18" stroke="none"/>'
    )

    line_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    parts.append(
        f'<path d="{line_d}" fill="none" stroke="{TITLE}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    max_i = max(range(n), key=lambda i: weekly_totals[i][1])
    for i, (x, y) in enumerate(points):
        is_max = i == max_i and weekly_totals[i][1] > 0
        color = ACCENT if is_max else TITLE
        r = 3 if is_max else 1.6
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'stroke="{BG}" stroke-width="0.8">'
            f'<title>{weekly_totals[i][0]}: {weekly_totals[i][1]}</title>'
            f'</circle>'
        )

    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title="Weekly trend (last 26 weeks)",
                subtitle=f"red dot = peak week · {today}")


# -------------------------------------------------------------- card 7: activity-graph (780x150)
def render_activity_graph(s: dict) -> str:
    width = 780
    height = 150
    days = s["days"]
    if not days:
        return card(width, height, "", title="Contribution heatmap")

    max_count = max((c for _, c, _ in days), default=0)

    columns: list[list[tuple[str, int, int]]] = []
    last_week_start: datetime.date | None = None
    for date_str, count, weekday in days:
        d = datetime.date.fromisoformat(date_str)
        week_start = d - datetime.timedelta(days=weekday)
        if week_start != last_week_start:
            columns.append([])
            last_week_start = week_start
        columns[-1].append((date_str, count, weekday))

    n_cols = len(columns)
    cell = 11
    gap = 2
    label_left = 28
    label_top = 60
    grid_w = n_cols * (cell + gap)
    margin_left = (width - grid_w - label_left - 80) / 2 + label_left
    if margin_left < label_left:
        margin_left = label_left

    parts: list[str] = []

    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for wd, label in dow_labels.items():
        y = label_top + wd * (cell + gap) + cell - 2
        parts.append(
            f'<text x="{margin_left - 4}" y="{y}" fill="{MUTED}" font-size="9" '
            f'text-anchor="end">{label}</text>'
        )

    month_seen: set[int] = set()
    for col_idx, col in enumerate(columns):
        if not col:
            continue
        d = datetime.date.fromisoformat(col[0][0])
        if d.month not in month_seen and d.day <= 7:
            month_seen.add(d.month)
            x = margin_left + col_idx * (cell + gap)
            parts.append(
                f'<text x="{x}" y="{label_top - 6}" fill="{MUTED}" font-size="9">'
                f'{d.strftime("%b")}</text>'
            )

    for col_idx, col in enumerate(columns):
        for date_str, count, weekday in col:
            x = margin_left + col_idx * (cell + gap)
            y = label_top + weekday * (cell + gap)
            color = heat_color(count, max_count)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'rx="2" fill="{color}">'
                f'<title>{date_str}: {count} contribution{"s" if count != 1 else ""}</title>'
                f'</rect>'
            )

    legend_x = margin_left + grid_w + 12
    parts.append(
        f'<text x="{legend_x}" y="{label_top + 8}" fill="{MUTED}" font-size="9">Less</text>'
    )
    for i, c in enumerate(HEAT):
        parts.append(
            f'<rect x="{legend_x + 28 + i * (cell + 2)}" y="{label_top + 1}" '
            f'width="{cell}" height="{cell}" rx="2" fill="{c}"/>'
        )
    parts.append(
        f'<text x="{legend_x + 28 + len(HEAT) * (cell + 2) + 2}" '
        f'y="{label_top + 8}" fill="{MUTED}" font-size="9">More</text>'
    )

    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title="Contribution heatmap (last 12 months)",
                subtitle=f"top 15% of any day plotted in red · updated {today}")


# -------------------------------------------------------------- card 8: top-repos
def render_top_repos(s: dict) -> str:
    width = 700
    repos = sorted(s["repos_meta"], key=lambda r: -r["stargazerCount"])[:5]
    height = 50 + len(repos) * 36 + 26

    parts: list[str] = []
    y = 60
    for r in repos:
        name = r["name"]
        desc = (r.get("description") or "").strip()
        if len(desc) > 78:
            desc = desc[:75] + "…"
        stars = r["stargazerCount"]
        forks = r["forkCount"]
        primary = r.get("primaryLanguage") or {}
        lang_name = primary.get("name") or "—"
        lang_color = primary.get("color") or LIGHT

        parts.append(
            f'<a xlink:href="{escape(r["url"])}" target="_blank">'
            f'<text x="22" y="{y}" fill="{TITLE}" font-size="12" '
            f'font-weight="700">{escape(name)}</text></a>'
        )
        parts.append(
            f'<text x="{width - 22}" y="{y}" fill="{MUTED}" font-size="10" '
            f'text-anchor="end">★ {stars}  ·  ⑂ {forks}</text>'
        )
        if desc:
            parts.append(
                f'<text x="22" y="{y + 14}" fill="{TEXT}" font-size="10">'
                f'{escape(desc)}</text>'
            )
        dot_y = y + 28
        parts.append(
            f'<circle cx="28" cy="{dot_y - 4}" r="3.5" fill="{lang_color}"/>'
            f'<text x="38" y="{dot_y}" fill="{MUTED}" font-size="9">'
            f'{escape(lang_name)}</text>'
        )
        y += 36

    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title="Top repositories",
                subtitle=f"by stars · updated {today}")


# -------------------------------------------------------------- card 9: repo-tiles
def render_repo_tiles(s: dict) -> str:
    width = 700
    repos = sorted(
        s["repos_meta"],
        key=lambda r: (
            (r.get("primaryLanguage") or {}).get("name") or "zzz",
            -r["stargazerCount"],
        ),
    )
    if not repos:
        return card(width, 180, "", title="Repository portfolio")

    n = len(repos)
    # Pick a column count that fills rows evenly (avoids a stranded last row).
    if n <= 6:
        cols = n
    elif n % 8 == 0:
        cols = 8
    elif n % 9 == 0:
        cols = 9
    elif n <= 18:
        cols = 8 if n % 8 >= n % 9 else 9
    else:
        cols = 13
    rows = math.ceil(n / cols)
    tile = 42
    gap = 8
    grid_w = cols * (tile + gap) - gap
    grid_h = rows * (tile + gap) - gap
    margin_top = 50
    margin_left = (width - grid_w) / 2

    parts: list[str] = []
    for i, r in enumerate(repos):
        col = i % cols
        row = i // cols
        x = margin_left + col * (tile + gap)
        y = margin_top + row * (tile + gap)
        primary = r.get("primaryLanguage") or {}
        color = primary.get("color") or LIGHT
        lang = primary.get("name") or "—"
        stars = r["stargazerCount"]

        label = "".join(ch for ch in r["name"] if ch.isalnum())[:2].upper() or "?"

        parts.append(
            f'<a xlink:href="{escape(r["url"])}" target="_blank">'
            f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" '
            f'rx="6" fill="{color}" fill-opacity="0.85" '
            f'stroke="{LIGHT}" stroke-width="0.5">'
            f'<title>{escape(r["name"])} · {escape(lang)} · ★ {stars}</title>'
            f'</rect>'
            f'<text x="{x + tile/2}" y="{y + tile/2 + 4}" fill="white" '
            f'font-size="12" font-weight="700" text-anchor="middle" '
            f'pointer-events="none">{escape(label)}</text>'
            f'</a>'
        )

    height = margin_top + grid_h + 30
    today = datetime.date.today().isoformat()
    return card(width, height, "".join(parts),
                title=f"Repository portfolio — {n} public repos",
                subtitle=f"each tile coloured by primary language · {today}")


# ----------------------------------------------------------------- main
def main() -> None:
    print(f"fetching public stats for {USER}…")
    user = fetch()
    s = aggregate(user)

    print(f"  stars={s['stars']}  repos={s['repos']}  "
          f"commits(yr)={s['commits']}  prs={s['prs']}  "
          f"contribs={s['total_contributions']}  "
          f"streak now/longest={s['current_streak']}/{s['longest_streak']}")
    print(f"  top languages: {[(n, f'{p:.1f}%') for n, _, p in s['languages'][:5]]}")

    cards = [
        ("stats.svg",                render_stats(s)),
        ("top-langs.svg",            render_languages(s)),
        ("streak.svg",               render_streak(s)),
        ("weekday-distribution.svg", render_weekday_distribution(s)),
        ("cumulative-curve.svg",     render_cumulative_curve(s)),
        ("weekly-trend.svg",         render_weekly_trend(s)),
        ("activity-graph.svg",       render_activity_graph(s)),
        ("top-repos.svg",            render_top_repos(s)),
        ("repo-tiles.svg",           render_repo_tiles(s)),
    ]
    for name, svg in cards:
        (OUT / name).write_text(svg)
    print(f"wrote {len(cards)} SVGs to {OUT.resolve()}")


if __name__ == "__main__":
    main()
