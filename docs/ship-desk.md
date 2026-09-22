---
title: Ship Desk
---

# Ship Desk

A portable tool so builders do not abandon the work they already started.

## The problem

Cloud agents and local chats start PRs faster than humans review them. Ideas pile up as drafts. The next session starts something new. Products stall with 80 open PRs, most drafts.

## The loop

```text
see unfinished work → pick one per repo → finish or park → only then start new
```

"Clean up all the time" means **close the loop**, not delete history.

Finishing is either:

- merge after review, or
- close the draft and write one line why it died

Both keep the idea from rotting in the sidebar.

## Run

```bash
python3 -m repo_next_steps.ship_desk <github-owner>
```

Schedule the same way as the [morning board](morning-board-schedule.md). Pair them: morning board = what changed; ship desk = what is still open.

## Product

| Free | Later |
| --- | --- |
| CLI + skill on any agent host | Hosted desk for a team org |
| Rules in `data/ship-rules.json` | Branch + issue coverage with a token |
| Manual confirm to merge/close | CodeFriends nudge when a repo exceeds N drafts |

Do not sell an auto-merger. Sell staying on top of *their* ideas.
