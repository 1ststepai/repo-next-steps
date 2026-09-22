---
name: ship-desk
description: Keep a builder shipping by finding started-but-unfinished GitHub work (open and draft PRs). Print one finish-or-park plan per repo. Never merge or close without the user. Use when they feel buried in agents, drafts, or abandoned ideas.
---

# Ship Desk

## Purpose

People lose products in unattended PRs and cloud agents that never land. Ship Desk turns that pile into a short plan: **finish this, park that, stop the duplicate.**

It is a closer, not a janitor that force-merges at dawn.

## When to use

- Morning session, or "what did we start and not finish?"
- After a week of Cursor Cloud Agents
- Before starting *new* work on a repo that already has drafts

## Steps

1. Run (preferred):

```bash
python3 -m repo_next_steps.ship_desk 1ststepai
```

2. If you cannot run it, search `org:<owner> is:pr is:open` and apply the same rules.
3. For each repo, name **one** PR to finish (review → merge or close) and park the rest.
4. Flag drafts untouched for 7+ days as stop/close candidates — ask the user; do not close them yourself.
5. If they want a new feature on a repo with a tall draft stack, refuse the new agent until the stack shrinks.
6. Auto Model Router: this task is `fast / local` and read-only unless they confirm a merge.

## Output shape

```markdown
# Ship Desk — <owner>
## Finish today (one per repo)
## Stop or close
## Parked
```

## Do not

- Do not merge, squash, or close PRs without an explicit "close #N" / "merge #N".
- Do not open a new cloud agent to "catch up the list."
- Do not treat inventory/read-only scans as ship work.
- Do not rewrite git history every morning.
