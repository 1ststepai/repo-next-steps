#!/usr/bin/env python3
"""Small checks for the checklist engine. Run: python3 tests/test_engine.py"""

from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from repo_next_steps.engine import (
    evaluate,
    facts_from_snapshot,
    load_fixture,
    load_rules,
    parse_repo_url,
    render,
)


class ParseUrlTests(unittest.TestCase):
    def test_https(self):
        self.assertEqual(
            parse_repo_url("https://github.com/octocat/Hello-World"),
            ("octocat", "Hello-World"),
        )

    def test_git_suffix_and_slash(self):
        self.assertEqual(
            parse_repo_url("https://github.com/octocat/Hello-World.git/"),
            ("octocat", "Hello-World"),
        )

    def test_short(self):
        self.assertEqual(parse_repo_url("octocat/Hello-World"), ("octocat", "Hello-World"))

    def test_rejects_ssh(self):
        with self.assertRaises(ValueError):
            parse_repo_url("git@github.com:octocat/Hello-World.git")


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules()

    def _result(self, name: str):
        snap = load_fixture(name)
        facts = facts_from_snapshot(snap, self.rules)
        return evaluate(facts, self.rules)

    def test_hello_world_priorities(self):
        result = self._result("hello-world")
        ids = [item["id"] for item in result["actions"]]
        self.assertIn("readme", ids)
        self.assertIn("license", ids)
        self.assertIn("gitignore", ids)
        self.assertIn("ci", ids)
        self.assertIn("community", ids)
        self.assertIn("stale", ids)
        self.assertNotIn("empty", ids)
        self.assertNotIn("secrets", ids)
        license_item = next(i for i in result["actions"] if i["id"] == "license")
        self.assertEqual(license_item["priority"], "now")
        ci_item = next(i for i in result["actions"] if i["id"] == "ci")
        self.assertEqual(ci_item["priority"], "later")
        text = render(result, self.rules, demo=True)
        self.assertIn("Do next", text)
        self.assertIn("not a score", text.lower())
        self.assertIn("AI User Starter Kit", text)
        self.assertIn("CodeFriends", text)
        self.assertNotIn("hire us", text.lower())
        self.assertNotIn("/100", text)
        saved = (ROOT / "fixtures" / "hello-world.report.txt").read_text(encoding="utf-8")
        self.assertEqual(text, saved)

    def test_starter_kit_basics_ok(self):
        result = self._result("starter-kit")
        ids = [item["id"] for item in result["actions"]]
        self.assertNotIn("readme", ids)
        self.assertNotIn("license", ids)
        self.assertNotIn("empty", ids)
        self.assertNotIn("secrets", ids)
        self.assertNotIn("community", ids)
        self.assertIn("gitignore", ids)
        self.assertIn("ci", ids)
        okay = " ".join(result["okay"])
        self.assertIn("README", okay)
        self.assertIn("LICENSE", okay)

    def test_secret_filename_is_careful(self):
        snap = load_fixture("hello-world")
        snap = deepcopy(snap)
        snap["contents"].append({"name": ".env", "type": "file"})
        snap["contents"].append({"name": ".env.example", "type": "file"})
        facts = facts_from_snapshot(snap, self.rules)
        self.assertEqual(facts["secret_names"], [".env"])
        result = evaluate(facts, self.rules)
        secret = next(i for i in result["actions"] if i["id"] == "secrets")
        self.assertIn(".env", secret["why"])
        self.assertNotIn("audit", secret["why"].lower().replace("not a security audit", ""))
        self.assertIn("not a security audit", secret["why"].lower())

    def test_empty_repo_short_circuits(self):
        snap = {
            "repo": {
                "full_name": "someone/new",
                "html_url": "https://github.com/someone/new",
                "default_branch": "main",
                "license": None,
                "open_issues_count": 0,
                "has_issues": True,
                "forks_count": 0,
                "stargazers_count": 0,
            },
            "contents": [],
            "readme": None,
            "gitignore": None,
            "workflows": None,
        }
        facts = facts_from_snapshot(snap, self.rules)
        self.assertTrue(facts["is_empty"])
        result = evaluate(facts, self.rules)
        self.assertEqual([i["id"] for i in result["actions"]], ["empty"])


if __name__ == "__main__":
    unittest.main()
