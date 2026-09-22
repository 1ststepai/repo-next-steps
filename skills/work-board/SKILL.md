---
name: work-board
description: When the user is lost across many cloud agents or open PRs, print a Work Board. Do not merge stacks of drafts. One next review per repo.
---

# Work Board

## When to use

The user has a long Cursor Cloud Agent list, many draft PRs, or asks "what should we do next across repos."

## Steps

1. Say clearly: this board reads **GitHub open PRs**, not the Cursor agent runtime.
2. If you can run shell:
   `python3 -m repo_next_steps.work_board 1ststepai`
   (from a clone of this repo; `GITHUB_TOKEN` optional).
3. Group by repo. For each repo, recommend **one** next action.
4. If a repo has many drafts: pick the newest related PR; leave the rest parked.
5. If work is already on `main` (closed/merged PRs with the same title), say **stop the agent**.
6. Do not merge unless the user names a PR number.

## Do not

- Do not launch new cloud agents to "finish the list."
- Do not mass-merge drafts.
- Do not claim you can see Cursor's private agent UI.
