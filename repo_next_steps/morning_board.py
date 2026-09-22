#!/usr/bin/env python3
"""Morning Work Board — PRs + last-day commits for one GitHub owner.

Portable: any agent that can run Python 3. Does not merge. Does not talk to Grok.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from repo_next_steps.work_board import _headers, fetch_open_prs, render

COMMIT_API = "https://api.github.com/search/commits"


def fetch_commits(owner: str, since: str, per_page: int = 25) -> List[Dict[str, Any]]:
    q = f"org:{owner} committer-date:>={since}"
    params = urllib.parse.urlencode({"q": q, "per_page": per_page, "sort": "committer-date"})
    req = urllib.request.Request(
        f"{COMMIT_API}?{params}",
        headers={**_headers(), "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            q = f"user:{owner} committer-date:>={since}"
            params = urllib.parse.urlencode({"q": q, "per_page": per_page})
            req = urllib.request.Request(
                f"{COMMIT_API}?{params}",
                headers={**_headers(), "Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        else:
            raise
    return list(data.get("items") or [])


def render_commits(items: List[Dict[str, Any]]) -> str:
    lines = ["## Commits since yesterday", ""]
    if not items:
        lines.append("_None found on the public search (private repos need GITHUB_TOKEN)._")
        lines.append("")
        return "\n".join(lines)
    for it in items[:25]:
        repo = (it.get("repository") or {}).get("full_name") or "?"
        msg = ((it.get("commit") or {}).get("message") or "").split("\n", 1)[0][:80]
        sha = (it.get("sha") or "")[:7]
        lines.append(f"- `{sha}` {repo} — {msg}")
    lines.append("")
    return "\n".join(lines)


def build(owner: str) -> str:
    today = dt.datetime.now(dt.timezone.utc).date()
    since = (today - dt.timedelta(days=1)).isoformat()
    prs = fetch_open_prs(owner)
    body = render(owner, prs)
    try:
        commits = fetch_commits(owner, since)
        body += render_commits(commits)
    except urllib.error.HTTPError as exc:
        body += f"\n## Commits\n\nCommit search failed ({exc.code}). PRs section above still stands.\n"
    body += (
        "\n## Do today\n\n"
        "1. One repo, one PR. Park the rest.\n"
        "2. Stop agents whose titles already landed on main.\n"
        "3. Do not merge a draft stack.\n"
    )
    return f"_Generated {today.isoformat()} UTC. Advisory only._\n\n" + body


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print("Usage: python3 -m repo_next_steps.morning_board <owner>", file=sys.stderr)
        return 2
    owner = argv[1].strip().rstrip("/").split("/")[-1]
    try:
        sys.stdout.write(build(owner))
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error {exc.code}. Set GITHUB_TOKEN.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
