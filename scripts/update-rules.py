#!/usr/bin/env python3
"""Refresh data/rules.json from this repo's published main branch.

Default: fetch data/rules.json from GitHub raw (main only), keep it if newer.

No extra packages. No secrets. No vendor scraping.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "rules.json"
DEFAULT_URL = (
    "https://raw.githubusercontent.com/1ststepai/repo-next-steps/main/data/rules.json"
)
ALLOWED_PREFIX = "https://raw.githubusercontent.com/1ststepai/repo-next-steps/"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_version(raw: str) -> tuple[int, ...]:
    parts = []
    for piece in str(raw).split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def parse_day(raw: str) -> date:
    return date.fromisoformat(str(raw)[:10])


def is_newer(remote: dict, local: dict) -> bool:
    remote_day = parse_day(remote["updatedAt"])
    local_day = parse_day(local["updatedAt"])
    if remote_day != local_day:
        return remote_day > local_day
    return parse_version(remote["version"]) > parse_version(local["version"])


def validate(rules: dict) -> None:
    for key in ("version", "updatedAt", "checks"):
        if key not in rules:
            raise ValueError(f"rules missing {key}")
    parse_day(rules["updatedAt"])
    parse_version(rules["version"])
    if not isinstance(rules["checks"], list) or not rules["checks"]:
        raise ValueError("rules.checks must be a non-empty list")


def fetch_rules(url: str) -> dict:
    if not url.startswith(ALLOWED_PREFIX):
        raise ValueError(f"refusing URL (only {ALLOWED_PREFIX}… is allowed): {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "repo-next-steps-update/1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = resp.read().decode("utf-8")
    rules = json.loads(payload)
    validate(rules)
    return rules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--local",
        action="store_true",
        help="do not fetch; only validate the rules already on disk",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="GitHub raw URL for this repo's rules (default: main)",
    )
    args = parser.parse_args(argv)

    local = load_json(RULES_PATH)
    validate(local)
    print(f"Local rules: {local['version']} ({local['updatedAt']})")

    if args.local:
        print("Skipping fetch (--local). Local rules look valid.")
        return 0

    try:
        remote = fetch_rules(args.url)
    except urllib.error.HTTPError as exc:
        print(f"Remote rules not available ({exc.code} from {args.url}). Keeping local.")
        return 0
    except urllib.error.URLError as exc:
        print(f"Could not reach rules ({exc.reason}). Keeping local.")
        return 0
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Remote rules rejected ({exc}). Keeping local.")
        return 0

    print(f"Remote rules: {remote['version']} ({remote['updatedAt']})")
    if is_newer(remote, local):
        RULES_PATH.write_text(
            json.dumps(remote, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Updated {RULES_PATH.relative_to(ROOT)}")
    else:
        print("No newer rules; keeping local.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
