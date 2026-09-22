---
title: Work Board
---

# Work Board

A small desk for people with too many AI agents and too many draft PRs.

It answers: **which repo, which one PR, what to do.** It does not run Cursor Cloud Agents and it does not merge for you.

## Why this exists

A Cursor agent list is a stream. GitHub is the durable record. When those drift apart, people relaunch work that is already on `main` and stack eight draft PRs on one product.

Work Board reads open pull requests for an owner and prints:

- count per repo
- draft vs ready
- one next sentence per repo

## Run

```bash
cd repo-next-steps
python3 -m repo_next_steps.work_board 1ststepai
```

Optional token (higher rate limit; private PRs the token can see):

```bash
export GITHUB_TOKEN=$(gh auth token)
```

## Product shape (later money)

| Free | Later paid |
| --- | --- |
| This CLI + markdown board | Hosted board for a team org |
| Skill that tells agents to use the board | Slack/CodeFriends ping when a repo exceeds N drafts |
| Manual "stop the duplicate agent" | Cursor webhook if/when they expose one |

Do not productize a fake Cursor connector. Charge for a hosted org view and alerts.

## Related

- Snapshot board from 22 Sep 2026: [AGENT-BOARD-2026-09-22.md](AGENT-BOARD-2026-09-22.md)
- Starter kit [roadmap](https://github.com/1ststepai/ai-user-starter-kit/blob/main/docs/roadmap.md)
