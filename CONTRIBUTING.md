# Contributing

Thanks for helping keep this checklist useful for people who just started coding with AI.

This repo is **rules plus a thin Python CLI**. The value is the wording in [`data/rules.json`](data/rules.json), not a product to install.

## What to send

- Typos, broken links, and unclear sentences
- A check that scared someone or used a word they did not know
- A false alarm on a secret-looking filename (tell us the filename)
- Examples a brand-new user can follow without extra tools

Open an issue if you are unsure. Small pull requests are easier to review than large rewrites.

When you change a check’s wording or a threshold, bump `version` and `updatedAt` in `data/rules.json` and add a bullet to [CHANGELOG.md](CHANGELOG.md).

## Refreshing the rules

Checklist copy is not hand-curated in five places. It lives in [`data/rules.json`](data/rules.json).

1. Edit the check text, priorities, or filename lists there.
2. Bump `version` and `updatedAt` (`YYYY-MM-DD`).
3. Run `python3 scripts/update-rules.py --local` so the file still validates.
4. Run `python3 tests/test_engine.py` and `python3 -m repo_next_steps --demo`.
5. Add a line to `CHANGELOG.md`.

Readers later run `python3 scripts/update-rules.py` (no `--local`) to pull whatever is on `main`. The script only talks to this repo’s GitHub raw URL. Do not add scrapers or an OAuth login.

## Voice

Warm, clear, and practical. Short paragraphs. Define a jargon word the first time you use it. Never shame.

Please do **not**:

- Add consulting, booking, or “hire us” language
- Invent scores, grades, or security certifications
- Panic over a filename (`.env` is a heads-up, not a verdict)
- Scrape private repos or ask people to paste tokens into the tool
- Turn CodeFriends into a required step or a paywall
- Add a hosted app, login wall, or `npm install` as the core path
- Mention SwingTradePros or treat Auto Model Router as the product

## Docs map

| Path | Job |
| --- | --- |
| [README.md](README.md) | 30-second start and value |
| [index.html](index.html) | Static how-to + sample report |
| [data/rules.json](data/rules.json) | Checklist source of truth |
| [scripts/update-rules.py](scripts/update-rules.py) | Pull newer rules from `main` |
| [scripts/check.py](scripts/check.py) | Same as `python3 -m repo_next_steps` |
| [fixtures/](fixtures/) | Saved public-repo snapshots for `--demo` |
| [CHANGELOG.md](CHANGELOG.md) | What’s updated |

## Placeholders

Leave these as placeholders unless you have the real value from 1stStep.ai (Evan):

- CodeFriends **live invite URL** (repo link is the stand-in; `links.codeFriendsInvite` in `data/rules.json` is empty on purpose)
- Any extra community URL added later
- A dedicated product page on 1ststep.ai for this tool (README points at the GitHub repo)
- GitHub Pages, if we later serve `index.html` from the repo root or `/docs`

## License

By contributing, you agree your changes are released under the [MIT License](LICENSE).
