#!/usr/bin/env python3
# 重写 README 中 SHOWCASE 标记区间：左列=贡献过的明星项目，右列=代表作（仅本人仓库）
# 代表作排序：cards.config.json 配置优先，其余按 star 降序

import json
import os
import re
import sys
import urllib.request

USER = os.environ.get("CARD_USER", "fangfengxiang")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STAR_THRESHOLD = 50
STAR_PROJECTS_LIMIT = 8
REPOS_LIMIT = 6
CONFIG_PATH = "cards.config.json"
README_PATH = "README.md"

HDRS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "profile-cards",
}
if TOKEN:
    HDRS["Authorization"] = f"Bearer {TOKEN}"


def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def trunc(s, n):
    s = md_escape(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def fetch_contributions():
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


def order_own_repos(own):
    """配置顺序优先，其余按 star 降序（fetch 时已按 star 排序）。"""
    try:
        with open(CONFIG_PATH) as f:
            preferred = json.load(f).get("repos", [])
    except FileNotFoundError:
        preferred = []
    by_name = {r["full"].split("/", 1)[1]: r for r in own}
    ordered = [by_name.pop(n) for n in preferred if n in by_name]
    ordered.extend(by_name.values())
    return ordered[:REPOS_LIMIT]


def build_table(star_rows, own_rows):
    lines = [
        "| 🏆 贡献过的明星项目 | 🛠 代表作 |",
        "| --- | --- |",
    ]
    n = max(len(star_rows), len(own_rows))
    for i in range(n):
        left = ""
        if i < len(star_rows):
            r = star_rows[i]
            left = (f"**[{r['full']}](https://github.com/{r['full']})** "
                    f"⭐ {r['stars']} · {r['commits']} 提交 · {r['prs']} PR")
        right = ""
        if i < len(own_rows):
            r = own_rows[i]
            meta = " · ".join(p for p in [r["lang"], trunc(r["desc"], 40)] if p)
            right = (f"**[{r['full']}](https://github.com/{r['full']})** "
                     f"⭐ {r['stars']}")
            if meta:
                right += f"<br>{meta}"
        lines.append(f"| {left} | {right} |")
    return "\n".join(lines)


def main():
    star_rows = fetch_contributions()
    own_rows = order_own_repos(fetch_own_repos())
    block = build_table(star_rows, own_rows)

    with open(README_PATH) as f:
        readme = f.read()
    new_readme, count = re.subn(
        r"<!-- SHOWCASE:START -->.*?<!-- SHOWCASE:END -->",
        f"<!-- SHOWCASE:START -->\n{block}\n<!-- SHOWCASE:END -->",
        readme,
        flags=re.S,
    )
    if count == 0:
        print("error: SHOWCASE markers not found in README.md", file=sys.stderr)
        sys.exit(1)
    with open(README_PATH, "w") as f:
        f.write(new_readme)
    print(f"star projects: {len(star_rows)}, own repos: {len(own_rows)}")


if __name__ == "__main__":
    main()
