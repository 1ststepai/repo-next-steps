#!/usr/bin/env python3
"""Audit a single pull request before anyone calls it finished.

Hard-gate secrets, drafts, and dirty merge state. Never recommends folding
this PR into a different branch.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple

from repo_next_steps.work_board import _headers

SECRET_HINTS = (
    ".env",
    "credentials",
    "id_rsa",
    "secret",
    ".pem",
    "auth.json",
    "service-account",
)
RISK_PATHS = (
    ".github/workflows/",
    "auth",
    "payment",
    "webhook",
)


def _get(url: str) -> Any:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_pr(owner: str, repo: str, number: int) -> Dict[str, Any]:
    return _get(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}")


def fetch_files(owner: str, repo: str, number: int) -> List[Dict[str, Any]]:
    return list(_get(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files?per_page=100"))


def audit(owner: str, repo: str, number: int) -> Dict[str, Any]:
    """Return gate, reasons, stats. On API failure, hard-gate."""
    reasons: List[str] = []
    try:
        pr = fetch_pr(owner, repo, number)
        files = fetch_files(owner, repo, number)
    except urllib.error.HTTPError as exc:
        return {
            "gate": "hard_gate",
            "reasons": [f"could not load PR #{number} ({exc.code}); do not merge"],
            "draft": True,
            "files": 0,
        }

    draft = bool(pr.get("draft"))
    state = pr.get("mergeable_state") or "unknown"
    title = pr.get("title") or ""
    body = pr.get("body") or ""
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    commits = int(pr.get("commits") or 0)

    if draft:
        reasons.append("still a draft — not mergeable")
    if state in ("dirty", "blocked", "behind", "unstable"):
        reasons.append(f"mergeable_state={state}")
    if commits == 0:
        reasons.append("no commits")
    if additions + deletions > 2000:
        reasons.append(f"huge diff +{additions}/-{deletions} — review alone, do not fold into another PR")

    secret_hits = []
    risk_hits = []
    names = []
    for f in files:
        name = (f.get("filename") or "").lower()
        names.append(name)
        if any(h in name for h in SECRET_HINTS):
            secret_hits.append(name)
        if any(h in name for h in RISK_PATHS):
            risk_hits.append(name)
    if secret_hits:
        reasons.append("secret-looking paths: " + ", ".join(secret_hits[:5]))
    if risk_hits:
        reasons.append("auth/workflow/payment paths changed — confirm required")

    # One idea: title + file set should not look like two products glued together
    if " and " in title.lower() and additions > 400:
        reasons.append("title looks like two jobs in one PR — split, do not merge-as-is")

    if secret_hits or draft or state in ("dirty", "blocked") or commits == 0:
        gate = "hard_gate"
    elif reasons:
        gate = "confirm"
    else:
        gate = "confirm"  # ship desk never auto-merges

    return {
        "gate": gate,
        "reasons": reasons or ["no automated red flags; human review still required"],
        "draft": draft,
        "mergeable_state": state,
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
        "files": len(files),
        "title": title,
        "do_not": "Do not cherry-pick or squash this into a different PR. Finish or close this number.",
    }


def format_audit(owner: str, repo: str, number: int, result: Dict[str, Any]) -> str:
    lines = [
        f"### Audit {owner}/{repo}#{number} — {result.get('gate')}",
        "",
        f"- files {result.get('files')}  commits {result.get('commits')}  "
        f"+{result.get('additions')}/-{result.get('deletions')}  "
        f"mergeable={result.get('mergeable_state')}",
    ]
    for r in result.get("reasons") or []:
        lines.append(f"- {r}")
    lines.append(f"- {result.get('do_not')}")
    return "\n".join(lines) + "\n"
