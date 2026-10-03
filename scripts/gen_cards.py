#!/usr/bin/env python3
# 生成主页动态卡片：贡献过的明星项目 + 代表作
# 数据源：GitHub Search API（merged PR / commit）+ Repos API（star 数）

import html
import json
import os
import sys
import urllib.request

USER = os.environ.get("CARD_USER", "fangfengxiang")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STAR_PROJECTS_LIMIT = 8
REPOS_LIMIT = 6
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
        "title": "#1f2328", "text": "#57606a", "name": "#1f2328",
        "star": "#e3b341",
    },
    "dark": {
        "card_bg": "#161b22", "card_border": "#30363d",
        "title": "#e6edf3", "text": "#8b949e", "name": "#e6edf3",
        "star": "#e3b341",
    },
}


def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def esc(s):
    return html.escape(s or "", quote=True)


def trunc(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


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
    rows.sort(key=lambda r: -r["stars"])
    return rows


def fetch_own_repos():
    data = api(f"https://api.github.com/users/{USER}/repos"
               f"?per_page=100&type=owner")
    repos = []
    for r in data:
        if r["fork"] or r["name"] == USER:
            continue
        repos.append({
            "full": r["full_name"],
            "stars": r["stargazers_count"],
            "lang": r.get("language"),
            "desc": r.get("description"),
        })
    repos.sort(key=lambda r: -r["stars"])
    return repos


FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def star_projects_svg(rows, theme):
    rows = [r for r in rows if r["stars"] >= STAR_THRESHOLD][:STAR_PROJECTS_LIMIT]
    W, pad, row_h, gap = 840, 20, 52, 10
    head_h = 76
    body = len(rows) * (row_h + gap) if rows else 56
    H = pad * 2 + head_h + body
    t = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" '
        f'fill="{t["card_bg"]}" stroke="{t["card_border"]}"/>',
        f'<text x="{pad}" y="44" font-size="20" font-weight="600" '
        f'fill="{t["title"]}">🏆 贡献过的明星项目</text>',
        f'<text x="{pad}" y="70" font-size="13" fill="{t["text"]}">'
        f'参与过的高星开源仓库（提交 + PR）</text>',
    ]
    if not rows:
        parts.append(
            f'<text x="{pad}" y="{head_h + pad + 24}" font-size="14" '
            f'fill="{t["text"]}">暂无数据</text>')
    y = pad + head_h
    for r in rows:
        parts += [
            f'<rect x="{pad}" y="{y}" width="{W - pad*2}" height="{row_h}" '
            f'rx="10" fill="none" stroke="{t["card_border"]}"/>',
            f'<text x="{pad + 16}" y="{y + row_h//2 + 5}" font-size="15" '
            f'font-weight="500" fill="{t["name"]}">{esc(r["full"])}</text>',
            f'<text x="{W - pad - 16}" y="{y + row_h//2 + 5}" font-size="14" '
            f'text-anchor="end" fill="{t["text"]}">'
            f'<tspan fill="{t["star"]}">★</tspan> {r["stars"]}'
            f'  {r["commits"]} 提交 · {r["prs"]} PR</text>',
        ]
        y += row_h + gap
    parts.append("</svg>")
    return "\n".join(parts)


def repos_svg(contribs, own, theme):
    entries = []
    for r in contribs:
        if r["stars"] >= STAR_THRESHOLD:
            entries.append({**r, "meta": f'{r["prs"]} PR · {r["commits"]} 提交'})
    for r in own:
        if len(entries) >= REPOS_LIMIT:
            break
        meta_parts = ([r["lang"]] if r["lang"] else []) + [trunc(r["desc"], 42)]
        entries.append({**r, "meta": trunc("  ".join(p for p in meta_parts if p), 46)})
    entries = entries[:REPOS_LIMIT]

    W, pad, card_h, gap = 840, 20, 86, 14
    head_h = 76
    cols = 2
    card_w = (W - pad * 2 - gap) // cols
    rows_n = (len(entries) + cols - 1) // cols if entries else 1
    H = pad * 2 + head_h + rows_n * (card_h + gap)
    t = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" '
        f'fill="{t["card_bg"]}" stroke="{t["card_border"]}"/>',
        f'<text x="{pad}" y="44" font-size="20" font-weight="600" '
        f'fill="{t["title"]}">🛠 代表作</text>',
        f'<text x="{pad}" y="70" font-size="13" fill="{t["text"]}">'
        f'按实质贡献优先、高星影响辅助排序的代表项目</text>',
    ]
    if not entries:
        parts.append(
            f'<text x="{pad}" y="{head_h + pad + 24}" font-size="14" '
            f'fill="{t["text"]}">暂无数据</text>')
    for i, e in enumerate(entries):
        col, row = i % cols, i // cols
        x = pad + col * (card_w + gap)
        y = pad + head_h + row * (card_h + gap)
        parts += [
            f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" '
            f'rx="10" fill="none" stroke="{t["card_border"]}"/>',
            f'<text x="{x + 16}" y="{y + 32}" font-size="15" '
            f'font-weight="500" fill="{t["name"]}">'
            f'{esc(trunc(e["full"], 30))}</text>',
            f'<text x="{x + card_w - 16}" y="{y + 32}" font-size="14" '
            f'text-anchor="end" fill="{t["text"]}">'
            f'<tspan fill="{t["star"]}">★</tspan> {e["stars"]}</text>',
            f'<text x="{x + 16}" y="{y + 62}" font-size="13" '
            f'fill="{t["text"]}">{esc(e["meta"])}</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    contribs = fetch_contributions()
    own = fetch_own_repos()
    os.makedirs("cards", exist_ok=True)
    for theme in THEMES:
        suffix = "-dark" if theme == "dark" else ""
        with open(f"cards/star-projects{suffix}.svg", "w") as f:
            f.write(star_projects_svg(contribs, theme))
        with open(f"cards/repos{suffix}.svg", "w") as f:
            f.write(repos_svg(contribs, own, theme))
    print(f"star projects: {len(contribs)}, own repos: {len(own)}")


if __name__ == "__main__":
    main()
