# Agent board — 22 September 2026

Cursor Cloud Agents are not readable from GitHub. This board maps the visible agent list to repos and the next human step. Do not merge draft PRs from this file.

## Done on GitHub today (this conversation)

- `auto-model-router` PR #8 merged — local vs cloud mode on `main`
- AMR pointers on `1ststep-os`, `codefriends`, `agent-memory`, `main-website`
- `ai-user-starter-kit` 1.1.0 — skill-maker, file-organizer, weekly-brief, geo-block + [roadmap](https://github.com/1ststepai/ai-user-starter-kit/blob/main/docs/roadmap.md)

## Still live in Cursor (from the agent list)

Treat read-only inventory agents as **finished enough**. Do not relaunch them.

| Agent (truncated) | Repo | GitHub status | Next |
| --- | --- | --- | --- |
| STP SM Birdeye+Shyft | swingtradepros | Draft [PR #290](https://github.com/1ststepai/swingtradepros/pull/290) | Review; do not merge drafts in bulk |
| STP SM usable paper UX | swingtradepros | Related drafts #286–#292 | Pick **one** STP PR to un-draft after a local run |
| Remove Steam Friends-style la… | codefriends | Tiny diff (+6/-6) | Confirm copy change, then merge if tests green |
| Savings Desk MVP | auto-model-router | [PR #5](https://github.com/1ststepai/auto-model-router/pull/5) closed | Leave closed unless you want the desk on `main` |
| Boundary-gated confirms | auto-model-router | #4/#6/#7 closed; already on `main` | No further agent |
| CodeFriends $0 deploy / Connect / persistence / Steam-style | codefriends | Open drafts [#16](https://github.com/1ststepai/codefriends/pull/16) [#18](https://github.com/1ststepai/codefriends/pull/18) [#25](https://github.com/1ststepai/codefriends/pull/25) | Un-draft **#25 School Paths** only after reading the pack |
| Resolve AMR marketplace PR #15 | auto-model-router | No open PR #15 on GitHub | Likely already landed or renamed; stop the agent |
| AMR marketplace / Codex live / neon logo / package plugins | auto-model-router | PRs #1–#3 closed | Done. Reinstall plugin from `main` |
| Sitewide SEO / Tools SEO / discoverability | main-website | Drafts [#11](https://github.com/1ststepai/main-website/pull/11) [#12](https://github.com/1ststepai/main-website/pull/12) [#9](https://github.com/1ststepai/main-website/pull/9) | One SEO PR, not three |
| Animate AMR / opt-in | auto-model-router + main-website | Check Tools page on site | Cosmetic; after SEO |
| STP overnight homepage / SM+Nova | swingtradepros | Drafts #281, #292 | After Smart Money paper, not before |
| Read-only scans: STP, creative, reddit-agent, LaunchAgents, growth-finder | those repos | Inventory only | File findings; do not start write agents |
| Stp system baseline | swingtradepros | Draft [PR #270](https://github.com/1ststepai/swingtradepros/pull/270) | Docs only |

## What to run next (order)

1. Reinstall AMR from `main` + `./scripts/apply.sh --no-open` on the laptop.
2. Close or ignore duplicate AMR cloud agents (marketplace, logo, Codex demo) — already merged historically.
3. CodeFriends: review PR #25, keep #16/#18 draft.
4. main-website: review PR #12 (discoverability) as the single SEO land.
5. swingtradepros: one paper-trading PR (#290 or #286), not the whole draft stack.
6. Point new humans at the [starter-kit roadmap](https://github.com/1ststepai/ai-user-starter-kit/blob/main/docs/roadmap.md).

## Honest limit

Grok cannot attach to Cursor Cloud Agent runtimes. Steering is GitHub PRs + this board. If an agent is still spinning on work that is already on `main`, stop it in Cursor.
