#!/usr/bin/env python3
"""Inspect a public GitHub repo and print a beginner checklist.

Uses GitHub's public API and this repo's data/rules.json.
No extra packages. No scores. No private-repo access.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "rules.json"
FIXTURES = ROOT / "fixtures"
USER_AGENT = "repo-next-steps/1 (1stStep.ai; +https://github.com/1ststepai/repo-next-steps)"
API = "https://api.github.com"
DEMO_SLUG = "octocat/Hello-World"

PRIORITY_RANK = {"now": 0, "soon": 1, "later": 2}


def load_rules(path: Path = RULES_PATH) -> dict:
    rules = json.loads(path.read_text(encoding="utf-8"))
    validate_rules(rules)
    return rules


def validate_rules(rules: dict) -> None:
    for key in ("version", "updatedAt", "checks", "links", "priorityLabels"):
        if key not in rules:
            raise ValueError(f"rules missing {key}")
    if not isinstance(rules["checks"], list) or not rules["checks"]:
        raise ValueError("rules.checks must be a non-empty list")


def parse_repo_url(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if not text:
        raise ValueError("Paste a public GitHub address, like https://github.com/owner/repo")
    if text.startswith("git@"):
        raise ValueError(
            "That looks like an SSH git address. Use the public web URL instead, "
            "like https://github.com/owner/repo"
        )
    for prefix in ("https://", "http://"):
        if text.lower().startswith(prefix):
            text = text[len(prefix) :]
    if text.lower().startswith("www."):
        text = text[4:]
    if text.lower().startswith("github.com/"):
        parts = text.split("/")
        if len(parts) < 3 or not parts[1] or not parts[2]:
            raise ValueError("That GitHub URL is missing the owner or repo name.")
        owner, repo = parts[1], parts[2]
    elif text.count("/") == 1 and " " not in text:
        owner, repo = text.split("/", 1)
    else:
        raise ValueError(
            "Please use a public GitHub URL such as https://github.com/owner/repo "
            "(or owner/repo)."
        )
    repo = repo.removesuffix(".git").strip()
    owner = owner.strip()
    blocked = {"settings", "marketplace", "topics", "orgs", "explore", "features"}
    if owner.lower() in blocked or not owner or not repo:
        raise ValueError("That does not look like an owner/repo pair.")
    return owner, repo


def _request(url: str, token: str | None) -> tuple[int, object]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {"message": body}
        return exc.code, payload


def fetch_snapshot(owner: str, repo: str, token: str | None = None) -> dict:
    status, data = _request(f"{API}/repos/{owner}/{repo}", token)
    if status == 404:
        raise ValueError(
            "We could not see that repo. It may be private, renamed, or mistyped. "
            "This tool only reads public GitHub repos."
        )
    if status == 403:
        raise ValueError(
            "GitHub asked us to slow down (rate limit). Wait a minute and try again, "
            "or set GITHUB_TOKEN to a personal token for a higher public-API limit. "
            "v1 still will not open private repos."
        )
    if status != 200 or not isinstance(data, dict):
        raise ValueError(f"GitHub returned an unexpected response ({status}).")
    if data.get("private"):
        raise ValueError(
            "That repo is private. v1 does not read private data. "
            "A later consent-connect path would let you choose to connect."
        )

    contents_status, contents = _request(f"{API}/repos/{owner}/{repo}/contents/", token)
    if contents_status == 404:
        contents = []
    elif contents_status != 200 or not isinstance(contents, list):
        contents = []

    readme = None
    rm_status, rm_data = _request(f"{API}/repos/{owner}/{repo}/readme", token)
    if rm_status == 200 and isinstance(rm_data, dict):
        text = ""
        download = rm_data.get("download_url")
        if download and str(download).startswith("https://raw.githubusercontent.com/"):
            try:
                req = urllib.request.Request(download, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
            except (urllib.error.URLError, urllib.error.HTTPError):
                text = ""
        readme = {
            "name": rm_data.get("name") or "README",
            "size": rm_data.get("size") or 0,
            "text": text,
        }

    gitignore = None
    gi_status, gi_data = _request(f"{API}/repos/{owner}/{repo}/contents/.gitignore", token)
    if gi_status == 200 and isinstance(gi_data, dict) and gi_data.get("download_url"):
        download = gi_data["download_url"]
        text = ""
        if str(download).startswith("https://raw.githubusercontent.com/"):
            try:
                req = urllib.request.Request(download, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
            except (urllib.error.URLError, urllib.error.HTTPError):
                text = ""
        gitignore = {"name": ".gitignore", "text": text}

    workflows = None
    names = [item.get("name", "") for item in contents] if isinstance(contents, list) else []
    if ".github" in names:
        wf_status, wf_data = _request(
            f"{API}/repos/{owner}/{repo}/contents/.github/workflows", token
        )
        if wf_status == 200 and isinstance(wf_data, list):
            workflows = [item.get("name", "") for item in wf_data if item.get("type") == "file"]
        else:
            workflows = []

    return {
        "repo": data,
        "contents": contents if isinstance(contents, list) else [],
        "readme": readme,
        "gitignore": gitignore,
        "workflows": workflows,
    }


def _parse_time(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _human_date(when: datetime) -> str:
    return when.strftime("%d %B %Y").lstrip("0")


def _is_secret_name(name: str, rules: dict) -> bool:
    looks = rules.get("secretLooks") or {}
    lower = name.lower()
    if name in (looks.get("okExact") or []) or lower in {
        n.lower() for n in (looks.get("okExact") or [])
    }:
        return False
    exact = {n.lower() for n in (looks.get("exact") or [])}
    if lower in exact:
        return True
    for suffix in looks.get("suffixes") or []:
        if lower.endswith(suffix.lower()) and not lower.endswith(".example" + suffix.lower()):
            if lower.endswith(".pub"):
                return False
            return True
    return False


def facts_from_snapshot(snapshot: dict, rules: dict) -> dict:
    repo = snapshot.get("repo") or {}
    contents = snapshot.get("contents") or []
    names = [item.get("name", "") for item in contents if item.get("name")]
    file_names = [item.get("name", "") for item in contents if item.get("type") == "file"]

    license_names = {n.lower() for n in (rules.get("licenseNames") or [])}
    contributing_names = {n.lower() for n in (rules.get("contributingNames") or [])}
    gitignore_names = {n.lower() for n in (rules.get("gitignoreNames") or [])}
    ci_root = {p.lower() for p in (rules.get("ciPaths") or []) if "/" not in p or p.count("/") == 0}

    license_meta = repo.get("license") or {}
    has_license = bool(license_meta.get("spdx_id") or license_meta.get("key"))
    if any(n.lower() in license_names for n in names):
        has_license = True

    has_contributing = any(n.lower() in contributing_names for n in names)
    has_gitignore = any(n.lower() in gitignore_names for n in names)
    gitignore_text = ((snapshot.get("gitignore") or {}).get("text") or "").strip()
    gitignore_useful = False
    if gitignore_text:
        for line in gitignore_text.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                gitignore_useful = True
                break

    has_ci = bool(snapshot.get("workflows"))
    for name in names:
        if name.lower() in ci_root or name in (rules.get("ciPaths") or []):
            has_ci = True
        if name == ".circleci":
            has_ci = True

    secrets = [n for n in file_names if _is_secret_name(n, rules)]

    readme = snapshot.get("readme")
    readme_text = (readme or {}).get("text") or ""
    has_readme = bool(readme) or any(n.lower().startswith("readme") for n in names)

    pushed = _parse_time(repo.get("pushed_at"))
    now = datetime.now(timezone.utc)
    days_quiet = None
    if pushed:
        days_quiet = max(0, (now - pushed).days)

    is_empty = not names and not has_readme
    if repo.get("default_branch") in (None, "") and not names:
        is_empty = True

    forks = int(repo.get("forks_count") or 0)
    stars = int(repo.get("stargazers_count") or 0)
    signals = rules.get("sharedSignals") or {}
    looks_shared = forks >= int(signals.get("minForks") or 1) or stars >= int(
        signals.get("minStars") or 5
    )

    return {
        "full_name": repo.get("full_name") or "",
        "html_url": repo.get("html_url") or "",
        "description": (repo.get("description") or "").strip(),
        "default_branch": repo.get("default_branch") or "",
        "pushed_at": pushed,
        "days_quiet": days_quiet,
        "open_issues": int(repo.get("open_issues_count") or 0),
        "has_issues": bool(repo.get("has_issues")),
        "forks": forks,
        "stars": stars,
        "looks_shared": looks_shared,
        "license_spdx": license_meta.get("spdx_id") if isinstance(license_meta, dict) else None,
        "has_license": has_license,
        "root_names": names,
        "has_readme": has_readme,
        "readme_text": readme_text,
        "has_gitignore": has_gitignore,
        "gitignore_useful": gitignore_useful,
        "has_ci": has_ci,
        "secret_names": secrets,
        "has_contributing": has_contributing,
        "is_empty": is_empty,
    }


def _rule(rules: dict, check_id: str) -> dict:
    for row in rules["checks"]:
        if row.get("id") == check_id:
            return row
    raise KeyError(check_id)


def _item(rule: dict, priority: str, title: str, why: str, good: str) -> dict:
    return {
        "id": rule["id"],
        "priority": priority,
        "title": title,
        "why": why,
        "goodEnough": good,
        "skipOk": rule.get("skipOk") or "",
    }


def evaluate(facts: dict, rules: dict) -> dict:
    actions: list[dict] = []
    okay: list[str] = []

    if facts["is_empty"]:
        rule = _rule(rules, "empty")
        actions.append(
            _item(rule, rule["priority"], rule["title"], rule["why"], rule["goodEnough"])
        )
        return {"facts": facts, "actions": actions, "okay": okay}

    # README
    rule = _rule(rules, "readme")
    text = facts["readme_text"].strip()
    min_chars = int(rules.get("readmeMinChars") or 80)
    if not facts["has_readme"]:
        actions.append(
            _item(
                rule,
                rule["priorityMissing"],
                rule["titleMissing"],
                rule["whyMissing"],
                rule["goodEnough"],
            )
        )
    elif len(text) < min_chars or text.count("\n") == 0 and len(text) < min_chars:
        why = rule["whyWeak"]
        if facts["description"]:
            why += " GitHub already has a one-line description you can paste in and expand."
        actions.append(
            _item(rule, rule["priorityWeak"], rule["titleWeak"], why, rule["goodEnough"])
        )
    else:
        okay.append("The README says what this project is.")

    # LICENSE
    rule = _rule(rules, "license")
    if facts["has_license"]:
        label = facts.get("license_spdx") or "a license"
        if label in ("NOASSERTION", "NONE"):
            label = "a license file"
        okay.append(f"A LICENSE is present ({label}).")
    else:
        priority = rule["priorityIfShared"] if facts["looks_shared"] else rule["priority"]
        actions.append(
            _item(rule, priority, rule["title"], rule["why"], rule["goodEnough"])
        )

    # Secrets — filenames only, no panic
    rule = _rule(rules, "secrets")
    if facts["secret_names"]:
        names = ", ".join(f"`{n}`" for n in facts["secret_names"][:5])
        actions.append(
            _item(
                rule,
                rule["priority"],
                rule["title"],
                rule["why"].replace("{names}", names),
                rule["goodEnough"],
            )
        )
    else:
        okay.append("No secret-looking filenames in the top folder (we only checked names).")

    # .gitignore
    rule = _rule(rules, "gitignore")
    if facts["has_gitignore"] and facts["gitignore_useful"]:
        okay.append("A .gitignore is present.")
    elif facts["has_gitignore"] and not facts["gitignore_useful"]:
        actions.append(
            _item(
                rule,
                rule["priority"],
                "Put one real line in .gitignore",
                "There is a .gitignore, but it has no rules yet — only blank lines or comments.",
                rule["goodEnough"],
            )
        )
    else:
        actions.append(
            _item(rule, rule["priority"], rule["title"], rule["why"], rule["goodEnough"])
        )

    # CI
    rule = _rule(rules, "ci")
    if facts["has_ci"]:
        okay.append("CI (a robot that runs checks) is already set up.")
    else:
        actions.append(
            _item(rule, rule["priority"], rule["title"], rule["why"], rule["goodEnough"])
        )

    # Issues / contributing — only when relevant
    rule = _rule(rules, "community")
    issues_relevant = facts["has_issues"] and facts["open_issues"] > 0 and facts["looks_shared"]
    contrib_relevant = facts["looks_shared"] and not facts["has_contributing"]
    if issues_relevant:
        actions.append(
            _item(
                rule,
                rule["priority"],
                rule["titleIssues"],
                rule["whyIssues"].replace("{count}", str(facts["open_issues"])),
                rule["goodEnoughIssues"],
            )
        )
    if contrib_relevant:
        actions.append(
            _item(
                rule,
                rule["priority"],
                rule["titleContributing"],
                rule["whyContributing"],
                rule["goodEnoughContributing"],
            )
        )
    if facts["has_contributing"]:
        okay.append("A CONTRIBUTING note is present.")

    # Stale — soft
    rule = _rule(rules, "stale")
    stale_days = int(rules.get("staleDays") or 180)
    if facts["days_quiet"] is not None and facts["days_quiet"] >= stale_days and facts["pushed_at"]:
        when = _human_date(facts["pushed_at"])
        actions.append(
            _item(
                rule,
                rule["priority"],
                rule["title"],
                rule["why"].replace("{when}", when),
                rule["goodEnough"],
            )
        )
    elif facts["pushed_at"] and facts["days_quiet"] is not None:
        okay.append(f"There is recent activity (last change {_human_date(facts['pushed_at'])}).")

    actions.sort(key=lambda row: PRIORITY_RANK.get(row["priority"], 9))
    return {"facts": facts, "actions": actions, "okay": okay}


def render(result: dict, rules: dict, *, demo: bool = False) -> str:
    facts = result["facts"]
    labels = rules.get("priorityLabels") or {}
    links = rules.get("links") or {}
    lines: list[str] = []
    lines.append("Repo Next Steps — 1stStep.ai")
    lines.append("")
    lines.append("This is a plain-English checklist of what this public repo needs next.")
    lines.append("It is not a score, not a grade, and not a security certification.")
    if demo:
        lines.append("Demo mode: using a saved snapshot, so you can see a sample without guessing.")
    lines.append("")
    lines.append(f"Looking at: {facts['full_name'] or '(unknown)'}")
    if facts["html_url"]:
        lines.append(f"Page: {facts['html_url']}")
    if facts["default_branch"]:
        lines.append(f"Main copy (default branch): {facts['default_branch']}")
    if facts["pushed_at"]:
        lines.append(f"Last saved change: {_human_date(facts['pushed_at'])}")
    lines.append("")
    lines.append("Do next")
    lines.append("=======")
    lines.append("")
    if not result["actions"]:
        lines.append("Nothing urgent. The basics look in place for week one.")
        lines.append("")
    else:
        for i, item in enumerate(result["actions"], start=1):
            band = labels.get(item["priority"], item["priority"])
            lines.append(f"{i}. {band} — {item['title']}")
            lines.append(f"   Why it matters: {item['why']}")
            lines.append(f"   Good enough for week one: {item['goodEnough']}")
            if item.get("skipOk"):
                lines.append(f"   Skip for now? {item['skipOk']}")
            lines.append("")

    if result["okay"]:
        lines.append("Looks okay")
        lines.append("==========")
        for note in result["okay"]:
            lines.append(f"- {note}")
        lines.append("")

    lines.append("Private repos")
    lines.append("This tool only reads public GitHub data. Private repos need a later")
    lines.append("consent-connect path (you would choose to connect). v1 does not log you in.")
    lines.append("")
    starter = links.get("starterKit") or "https://github.com/1ststepai/ai-user-starter-kit"
    lines.append("Keep learning: AI User Starter Kit")
    lines.append(starter)
    lines.append("")
    friends = links.get("codeFriends") or "https://github.com/1ststepai/codefriends"
    invite = (links.get("codeFriendsInvite") or "").strip()
    lines.append("Optional — CodeFriends")
    lines.append("If you want company while you learn — not a class, not a paywall —")
    lines.append(friends)
    if invite:
        lines.append(f"Invite: {invite}")
    else:
        lines.append("The live invite URL may be added later. You do not need to join to use this tool.")
    lines.append("")
    return "\n".join(lines)


def load_fixture(name: str) -> dict:
    path = Path(name)
    if not path.is_file():
        path = FIXTURES / name
    if not path.is_file() and not name.endswith(".json"):
        path = FIXTURES / f"{name}.json"
    if not path.is_file():
        raise ValueError(f"Could not find fixture {name}. Try hello-world or starter-kit.")
    return json.loads(path.read_text(encoding="utf-8"))


def _token() -> str | None:
    env = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return env.strip() if env else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="repo-next-steps",
        description=(
            "Paste a public GitHub repo URL. Get a plain-English, prioritized "
            "checklist of what that repo needs next."
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Public GitHub URL, such as https://github.com/owner/repo",
    )
    parser.add_argument(
        "--demo",
        nargs="?",
        const="hello-world",
        metavar="NAME",
        help="Print a sample report from a saved fixture (default: hello-world). No network.",
    )
    parser.add_argument(
        "--fixture",
        help="Path to a saved snapshot JSON (same as --demo NAME).",
    )
    parser.add_argument(
        "--rules",
        default=str(RULES_PATH),
        help="Path to data/rules.json (the checklist source of truth).",
    )
    args = parser.parse_args(argv)

    try:
        rules = load_rules(Path(args.rules))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not read rules: {exc}", file=sys.stderr)
        return 2

    demo = False
    try:
        if args.demo or args.fixture:
            demo = True
            snapshot = load_fixture(args.fixture or args.demo)
        elif args.url:
            owner, repo = parse_repo_url(args.url)
            snapshot = fetch_snapshot(owner, repo, _token())
        else:
            parser.print_help()
            print("\nQuick try: python3 -m repo_next_steps --demo")
            return 2
        facts = facts_from_snapshot(snapshot, rules)
        result = evaluate(facts, rules)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Could not reach GitHub ({exc.reason}). Check your network and try again.", file=sys.stderr)
        return 1

    print(render(result, rules, demo=demo), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
