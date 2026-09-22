#!/usr/bin/env python3
"""Ship Desk — unfinished GitHub work for one owner.

Finds open/draft PRs, ages them, audits the finish pick, and prints
finish / park / stop. Does not merge, close, or launch agents.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.error
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from repo_next_steps.audit import audit, format_audit
from repo_next_steps.work_board import _repo_name, fetch_open_prs

RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "ship-rules.json"


def load_rules() -> Dict[str, Any]:
    if RULES_PATH.is_file():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {"staleDays": 7, "stackWarn": 5, "auditPicks": True}


def _age_days(iso: str) -> int:
    if not iso:
        return 0
    raw = iso.replace("Z", "+00:00")
    try:
        then = dt.datetime.fromisoformat(raw)
    except ValueError:
        return 0
    if then.tzinfo is None:
        then = then.replace(tzinfo=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    return max(0, (now - then).days)


def classify(item: Dict[str, Any], stale_days: int) -> str:
    title = (item.get("title") or "").lower()
    draft = bool(item.get("draft")) or "draft" in title
    age = _age_days(item.get("updated_at") or "")
    stop_hints = (
        "already on main",
        "marketplace",
        "read-only",
        "inventory",
        "verification-only",
    )
    if any(h in title for h in stop_hints) and draft:
        return "stop"
    if age >= stale_days:
        return "finish" if not draft else "stop"
    if draft:
        return "wait"
    return "finish"


def plan(owner: str, items: List[Dict[str, Any]], rules: Dict[str, Any]) -> str:
    stale = int(rules.get("staleDays") or 7)
    stack_warn = int(rules.get("stackWarn") or 5)
    do_audit = bool(rules.get("auditPicks", True))
    by_repo: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for it in items:
        by_repo[_repo_name(it)].append(it)

    lines = [
        f"# Ship Desk — {owner}",
        "",
        "Unfinished pull requests. Advisory. Nothing was merged or closed.",
        "One idea stays on its own PR. Do not fold a parked draft into the finish pick.",
        "",
        f"Open PRs: {len(items)} across {len(by_repo)} repos. Stale after {stale} days.",
        "",
        "## Finish today (at most one per repo)",
        "",
    ]
    audited = 0
    for repo in sorted(by_repo, key=lambda r: -len(by_repo[r])):
        group = by_repo[repo]
        ranked: List[Tuple[str, Dict[str, Any]]] = [
            (classify(it, stale), it) for it in group
        ]
        pick = next((it for tag, it in ranked if tag == "finish"), None)
        if pick is None:
            pick = next((it for tag, it in ranked if tag == "wait"), group[0])
            tag = "wait"
        else:
            tag = "finish"
        extra = len(group) - 1
        age = _age_days(pick.get("updated_at") or "")
        draft = "draft" if pick.get("draft") else "open"
        num = pick.get("number")
        lines.append(
            f"- **{owner}/{repo}** → {tag} [{draft}] #{num} "
            f"{pick.get('title')} ({age}d) — {pick.get('html_url')}"
        )
        if extra:
            lines.append(
                f"  park {extra} other open PR(s). Do not squash them into #{num}."
            )
        if len(group) >= stack_warn:
            lines.append("  stack is too tall — no new agents here until this shrinks.")
        if do_audit and tag == "finish" and audited < 8 and isinstance(num, int):
            result = audit(owner, repo, num)
            lines.append("")
            lines.append(format_audit(owner, repo, num, result).rstrip())
            audited += 1
        lines.append("")
    if not by_repo:
        lines.append("_No open PRs. Do not invent work._")
        lines.append("")

    lines += ["## Stop or close (stale drafts / likely duplicates)", ""]
    stops = [it for it in items if classify(it, stale) == "stop"]
    if not stops:
        lines.append("_None flagged._")
    for it in stops[:20]:
        lines.append(
            f"- {_repo_name(it)} #{it.get('number')} {it.get('title')} — {it.get('html_url')}"
        )

    lines += [
        "",
        "## Rules",
        "",
        "1. Finish this PR or close it. Do not pour it into the next branch.",
        "2. Audit before merge: draft, dirty merge, secrets, auth/payment, huge mixed title.",
        "3. hard_gate means do not merge even if the user is in a hurry.",
        "4. Parked drafts stay parked until they get their own review.",
        "5. Closing with one sentence is allowed. Silent merge is not.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print("Usage: python3 -m repo_next_steps.ship_desk <owner>", file=sys.stderr)
        return 2
    owner = argv[1].strip().rstrip("/").split("/")[-1]
    rules = load_rules()
    try:
        items = fetch_open_prs(owner)
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error {exc.code}. Set GITHUB_TOKEN.", file=sys.stderr)
        return 1
    sys.stdout.write(plan(owner, items, rules))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
