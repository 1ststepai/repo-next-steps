# What’s updated

Newest first. Checklist wording and thresholds live in [`data/rules.json`](data/rules.json).

When 1stStep publishes newer rules on `main`, run `python3 scripts/update-rules.py` to pull them. No account. No extra packages.

## 1.0.0 — 2026-09-21

- First public tool: paste a public GitHub URL, get a Now / Soon / Later checklist
- Checks: README, LICENSE, empty repo, secret-looking filenames, .gitignore, CI, issues/contributing, quiet repos
- Self-update command: `python3 scripts/update-rules.py`
- `--demo` mode using saved snapshots of octocat/Hello-World and the AI User Starter Kit
