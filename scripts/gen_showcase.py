#!/usr/bin/env python3
# 重写 README 中 SHOWCASE 标记区间：贡献过的明星项目，渲染为 pin 图卡
# 数据来源：本人 merged PR + 外部仓库提交，按 star 降序，过滤 star < 阈值

import json
import os
import re
import sys
import urllib.request

USER = os.environ.get("CARD_USER", "fangfengxiang")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STAR_THRESHOLD = 50
STAR_PROJECTS_LIMIT = 8
README_PATH = "README.md"

HDRS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "profile-cards",
}
if TOKEN:
    HDRS["Authorization"] = f"Bearer {TOKEN}"

CARD = """  <a href="https://github.com/{full}">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/pin/?username={owner}&amp;repo={repo}&amp;theme=github_dark">
      <img src="https://github-readme-stats.vercel.app/api/pin/?username={owner}&amp;repo={repo}" alt="{full}">
    </picture>
  </a>"""


def api(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_contributions():
    contribs = {}
    try:
        data = api(f"https://api.github.com/search/issues"
                   f"?q=is:pr+author:{USER}+is:merged&per_page=100")
        for item in data.get("items", []):
            full = item["repository_url"].split("/repos/")[-1]
            if full.split("/")[0] == USER:
                continue
            contribs.setdefault(full, 0)
    except Exception as e:
        print(f"warn: search merged PRs failed: {e}", file=sys.stderr)

    try:
        data = api(f"https://api.github.com/search/commits"
                   f"?q=author:{USER}&per_page=100")
        for item in data.get("items", []):
            full = item["repository"]["full_name"]
            if full.split("/")[0] == USER:
                continue
            contribs.setdefault(full, 0)
    except Exception as e:
        print(f"warn: search commits failed: {e}", file=sys.stderr)

    rows = []
    for full in contribs:
        try:
            info = api(f"https://api.github.com/repos/{full}")
        except Exception as e:
            print(f"warn: repo {full} info failed: {e}", file=sys.stderr)
            continue
        rows.append({"full": full, "stars": info["stargazers_count"]})
    rows = [r for r in rows if r["stars"] >= STAR_THRESHOLD]
    rows.sort(key=lambda r: -r["stars"])
    return rows[:STAR_PROJECTS_LIMIT]


def build_cards(star_rows):
    lines = ['<p align="center">']
    for r in star_rows:
        owner, repo = r["full"].split("/", 1)
        lines.append(CARD.format(full=r["full"], owner=owner, repo=repo))
    lines.append("</p>")
    return "\n".join(lines)


def main():
    star_rows = fetch_contributions()
    block = build_cards(star_rows)

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
    print(f"star projects: {len(star_rows)}")


if __name__ == "__main__":
    main()
