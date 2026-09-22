#!/usr/bin/env python3
"""Work Board — open PRs across a GitHub user/org, grouped with a next-action hint.

Does not read Cursor Cloud Agents. Does not merge anything.
Public search by default. Optional GITHUB_TOKEN raises rate limits and can
see private PRs the token can access.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Any, Dict, List

API = "https://api.github.com/search/issues"


def _headers() -> Dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "1ststep-repo-next-steps-work-board",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_open_prs(owner: str, per_page: int = 50) -> List[Dict[str, Any]]:
    q = f"org:{owner} is:pr is:open"
    # Also try user: if org search is empty — caller can pass either.
    params = urllib.parse.urlencode({"q": q, "per_page": per_page, "sort": "updated"})
    req = urllib.request.Request(f"{API}?{params}", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Fallback: user qualifier
        if exc.code == 422:
            q = f"user:{owner} is:pr is:open"
            params = urllib.parse.urlencode({"q": q, "per_page": per_page, "sort": "updated"})
            req = urllib.request.Request(f"{API}?{params}", headers=_headers())
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        else:
            raise
    return list(data.get("items") or [])


def _repo_name(item: Dict[str, Any]) -> str:
    url = item.get("repository_url") or ""
    return url.rstrip("/").split("/")[-1] or "unknown"


def advise(items_for_repo: List[Dict[str, Any]]) -> str:
    n = len(items_for_repo)
    drafts = sum(1 for i in items_for_repo if i.get("draft") or "draft" in (i.get("title") or "").lower())
    if n >= 8:
        return "Too many open PRs. Pick ONE to un-draft. Do not merge the stack."
    if drafts == n and n > 1:
        return "All drafts. Review the newest; leave the rest draft."
    if n == 1:
        title = items_for_repo[0].get("title") or ""
        if items_for_repo[0].get("draft"):
            return f"Single draft. Read it before ready-for-review. ({title[:60]})"
        return f"One open PR. Review, then merge or close. ({title[:60]})"
    return "A few open PRs. Finish the oldest ready one; keep drafts parked."


def render(owner: str, items: List[Dict[str, Any]]) -> str:
    by_repo: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for it in items:
        by_repo[_repo_name(it)].append(it)
    lines = [
        f"# Work Board — {owner}",
        "",
        "Open pull requests only. Not Cursor Cloud Agents. Nothing was merged.",
        "",
        f"Count: {len(items)} open PRs across {len(by_repo)} repos.",
        "",
    ]
    for repo in sorted(by_repo, key=lambda r: (-len(by_repo[r]), r)):
        group = by_repo[repo]
        lines.append(f"## {owner}/{repo} ({len(group)})")
        lines.append("")
        lines.append(f"**Next:** {advise(group)}")
        lines.append("")
        for it in group[:12]:
            draft = "draft" if it.get("draft") else "open"
            num = it.get("number")
            title = (it.get("title") or "").strip()
            html = it.get("html_url") or ""
            lines.append(f"- [{draft}] #{num} {title} — {html}")
        if len(group) > 12:
            lines.append(f"- … {len(group) - 12} more")
        lines.append("")
    lines.append("Rule: one active review per repo. Stop agents whose work is already on main.")
    return "\n".join(lines) + "\n"


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print("Usage: python3 -m repo_next_steps.work_board <owner>\n"
              "Example: python3 -m repo_next_steps.work_board 1ststepai", file=sys.stderr)
        return 2
    owner = argv[1].strip().strip("/")
    if owner.startswith("https://"):
        # https://github.com/1ststepai → 1ststepai
        owner = owner.rstrip("/").split("/")[-1]
    try:
        items = fetch_open_prs(owner)
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error {exc.code}. Public search may be rate-limited; set GITHUB_TOKEN.", file=sys.stderr)
        return 1
    sys.stdout.write(render(owner, items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
