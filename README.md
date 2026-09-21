# Repo Next Steps

Paste a public GitHub URL. Get a plain-English checklist of what to do next.

Not a score. Not a security certification. Not a reason to hire anyone.

Built by [1stStep.ai](https://1ststep.ai).

## 30-second start

You need Python 3. Nothing to install.

```bash
git clone https://github.com/1ststepai/repo-next-steps
cd repo-next-steps
python3 -m repo_next_steps --demo
```

That prints a sample report from a saved snapshot of [octocat/Hello-World](https://github.com/octocat/Hello-World) — no network required.

On your own **public** repo:

```bash
python3 -m repo_next_steps https://github.com/owner/repo
```

Same command: `python3 scripts/check.py https://github.com/owner/repo`

You will know it worked when you see a numbered **Do next** list labeled Now / Soon / Later, plus a short **Looks okay** section.

## What you get

Each item has:

- a short title
- one sentence on why it matters
- what “good enough for week one” looks like
- when it is okay to skip

The checks (wording lives in [`data/rules.json`](data/rules.json)):

1. Has a README that says what the project is?
2. Has a LICENSE?
3. Is the repo empty? What is the default branch (the main copy)?
4. Are there obvious secret-looking filenames (`.env`, `credentials.json`)? Filenames only — no false panic.
5. Has a simple `.gitignore`?
6. Has any CI? If none: skip for week one unless sharing with others.
7. Open issues / contributing hints — only if they matter
8. Quiet / no recent commits — a soft note, not a warning

New to these words? A **README** is the first page people see. A **license** says how others may use your files. A **`.gitignore`** is a list of leftover files Git should not save. **CI** is a robot that runs checks when you save changes. A **commit** is a saved snapshot.

## Who this is for

People who are new to coding or AI coding and barely know what GitHub is. You cloned something (or the AI made a repo) and you want a calm next step — not a senior-engineer audit dump.

This tool is not a product pitch. You do not need an account.

## Public repos only

v1 reads GitHub’s **public** API and raw files. It will not open a private repo.

Private repos need a later **consent-connect** path (you would choose to connect). That is not built yet. Do not paste private tokens into this tool.

Optional: if you already use the GitHub CLI and hit a “slow down” message, you can raise the public-API limit with:

```bash
export GITHUB_TOKEN=$(gh auth token)
```

v1 still refuses private repos even if a token is set.

## Keep the checklist current

The questions and the wording live in [`data/rules.json`](data/rules.json). When that file changes on `main`, one command pulls it onto your clone:

```bash
python3 scripts/update-rules.py
```

Python 3 only. No packages. No account. It only talks to this repo’s GitHub raw URL.

You will know it worked when it prints the remote version and either `Updated data/rules.json` or `No newer rules; keeping local`.

**Publish path for 1stStep:** edit `data/rules.json` on `main`, bump `version` and `updatedAt`, run `python3 scripts/update-rules.py --local`. Everyone who runs the command later gets the new checklist. Future: richer checks. v1 does not scrape vendor docs or private data.

## Sample without guessing

```bash
python3 -m repo_next_steps --demo
python3 -m repo_next_steps --demo starter-kit
```

Saved snapshots live in [`fixtures/`](fixtures/). Reviewers can read those files and the printed report side by side.

A tiny static page ([`index.html`](index.html)) explains how to run the tool and shows a sample report. No backend. Open the file in a browser.

## What’s updated

Latest: **1.0.0** (21 September 2026) — first public checklist + rules v1.

Full list: [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE). Use it, copy it, and share it.

Fixes and clarifications are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

### Keep learning

If GitHub still feels new, start with the [AI User Starter Kit](https://github.com/1ststepai/ai-user-starter-kit) — a free first-week map, playbook, and safety notes. Same voice. No signup.

### Optional: CodeFriends

If you want company while you learn — not a class, not a paywall — [CodeFriends](https://github.com/1ststepai/codefriends) is a small, optional community for people figuring this out together.

The live invite URL may be added later. Until then, that repo is the placeholder. You do not need to join to use this tool.

1stStep.ai builds this tool and hosts the community invite.
