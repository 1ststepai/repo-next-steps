---
title: Schedule the morning board on any host
---

# Schedule the morning board on any host

The skill is instructions. The clock lives on **your** machine or CI.

## Cron (macOS / Linux)

```cron
0 8 * * 1-5 cd /path/to/repo-next-steps && GITHUB_TOKEN=$(gh auth token) python3 -m repo_next_steps.morning_board 1ststepai >> ~/.work-board.log
```

## Windows Task Scheduler

Program: `python3`  
Arguments: `-m repo_next_steps.morning_board 1ststepai`  
Start in: the clone. Trigger: weekdays 08:00 local.

## GitHub Actions (in this repo)

Workflow [`.github/workflows/morning-board.yml`](../.github/workflows/morning-board.yml) runs weekdays 12:00 UTC and writes `docs/boards/` as an artifact. It does not merge PRs. Enable Actions on the repo.

## Cursor

Copy `skills/morning-board/SKILL.md` to `.cursor/skills/morning-board/SKILL.md`. Optional always-apply rule: "At the start of the first weekday session, run the morning-board skill."

## Claude Code / Cowork

Copy to `.claude/skills/morning-board/SKILL.md`. If you use scheduled tasks / plugins, point the job at:
`python3 -m repo_next_steps.morning_board <owner>`

## Codex

Copy to `.agents/skills/morning-board/SKILL.md` and mention it in `AGENTS.md`.

## Gemini CLI / Spark

Copy to `.gemini/skills/morning-board/SKILL.md`. Spark schedules are host-side; the skill still only prints a board.

## What this is not

Not auto-squash. Not Grok-only. Not a Cursor Cloud Agent launcher.
