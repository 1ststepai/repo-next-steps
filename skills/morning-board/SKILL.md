---
name: morning-board
description: Each morning (or when the user asks what changed overnight), run the portable Work Board. Print open PRs by repo plus yesterday's commits. Do not merge. Works in Cursor, Claude, Codex, Gemini, or any agent that can run a local command or follow this file.
---

# Morning Work Board

Host-neutral skill. Not a Grok automation.

## When to use

- User says good morning, what landed, consolidate repos, or what should I review.
- A scheduled host job (cron, `gh` workflow, Claude scheduled task, Cursor rule) triggers this skill.

## Steps

1. If shell is allowed, from a clone of `1ststepai/repo-next-steps`:

```bash
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null)}"
python3 -m repo_next_steps.morning_board 1ststepai
```

Replace `1ststepai` with the user's GitHub owner.

2. If shell is not allowed, use the host's GitHub tool: search `org:<owner> is:pr is:open` and commits since yesterday. Group by repo.
3. For each repo with more than one open PR, name **one** next review. Park the rest.
4. If a title matches work already on `main`, say stop that agent.
5. Do not merge, force-push, or squash other people's branches.

## Suggestion line

If Auto Model Router is loaded: `Auto continues on fast / local — morning board is read-only.`

## Schedule (host, not this skill)

The skill does not register a timer. Copy one snippet from `docs/morning-board-schedule.md`.

## Do not

- Do not require Grok Automations.
- Do not launch cloud agents to refresh the board.
- Do not rewrite git history as "consolidation."
