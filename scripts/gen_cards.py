#!/usr/bin/env python3
# 生成主页动态卡片：贡献过的明星项目（SVG，明暗双主题）
# 数据源：GitHub Search API（merged PR / commit）+ Repos API（star 数）

import html
import json
import os
import sys
import urllib.request

USER = os.environ.get("CARD_USER", "fangfengxiang")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STAR_PROJECTS_LIMIT = 8
STAR_THRESHOLD = 50

HDRS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "profile-cards",
}
if TOKEN:
    HDRS["Authorization"] = f"Bearer {TOKEN}"

THEMES = {
    "light": {
        "card_bg": "#f6f8fa", "card_border": "#d0d7de",
        "text": "#57606a", "name": "#1f2328",
        "star": "#e3b341",
    },
    "dark": {
        "card_bg": "#161b22", "card_border": "#30363d",
        "text": "#8b949e", "name": "#e6edf3",
        "star": "#e3b341",
    },
}


def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def esc(s):
    return html.escape(s or "", quote=True)


def fetch_contributions():
    """返回 [{full, stars, prs, commits}]，按 stars 降序，仅含他人仓库。"""
    contribs = {}

    try:
        data = api(f"https://api.github.com/search/issues"
                   f"?q=is:pr+author:{USER}+is:merged&per_page=100")
        for item in data.get("items", []):
            full = item["repository_url"].split("/repos/")[-1]
            if full.split("/")[0] == USER:
                continue
            contribs.setdefault(full, {"prs": 0, "commits": 0})
            contribs[full]["prs"] += 1
    except Exception as e:
        print(f"warn: search merged PRs failed: {e}", file=sys.stderr)

    try:
        data = api(f"https://api.github.com/search/commits"
                   f"?q=author:{USER}&per_page=100")
        for item in data.get("items", []):
            full = item["repository"]["full_name"]
            if full.split("/")[0] == USER:
                continue
            contribs.setdefault(full, {"prs": 0, "commits": 0})
            contribs[full]["commits"] += 1
    except Exception as e:
        print(f"warn: search commits failed: {e}", file=sys.stderr)

    rows = []
    for full, counts in contribs.items():
        try:
            info = api(f"https://api.github.com/repos/{full}")
        except Exception as e:
            print(f"warn: repo {full} info failed: {e}", file=sys.stderr)
            continue
        rows.append({"full": full, "stars": info["stargazers_count"], **counts})
    rows = [r for r in rows if r["stars"] >= STAR_THRESHOLD]
    rows.sort(key=lambda r: -r["stars"])
    return rows[:STAR_PROJECTS_LIMIT]


FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def star_projects_svg(rows, theme):
    W, pad, row_h, gap = 840, 20, 52, 10
    body = len(rows) * (row_h + gap) if rows else 56
    H = pad * 2 + body
    t = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" '
        f'fill="{t["card_bg"]}" stroke="{t["card_border"]}"/>',
    ]
    if not rows:
        parts.append(
            f'<text x="{pad}" y="{pad + 24}" font-size="14" '
            f'fill="{t["text"]}">暂无数据</text>')
    y = pad
    for r in rows:
        parts += [
            f'<a href="https://github.com/{esc(r["full"])}">',
            f'<rect x="{pad}" y="{y}" width="{W - pad*2}" height="{row_h}" '
            f'rx="10" fill="none" stroke="{t["card_border"]}"/>',
            f'<text x="{pad + 16}" y="{y + row_h//2 + 5}" font-size="15" '
            f'font-weight="500" fill="{t["name"]}">{esc(r["full"])}</text>',
            f'<text x="{W - pad - 16}" y="{y + row_h//2 + 5}" font-size="14" '
            f'text-anchor="end" fill="{t["text"]}">'
            f'<tspan fill="{t["star"]}">★</tspan> {r["stars"]}'
            f'  {r["commits"]} 提交 · {r["prs"]} PR</text>',
            f'</a>',
        ]
        y += row_h + gap
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    rows = fetch_contributions()
    os.makedirs("cards", exist_ok=True)
    for theme in THEMES:
        suffix = "-dark" if theme == "dark" else ""
        with open(f"cards/star-projects{suffix}.svg", "w") as f:
            f.write(star_projects_svg(rows, theme))
    print(f"star projects: {len(rows)}")


if __name__ == "__main__":
    main()
