# Product Gate

Use this gate before expanding the skill beyond the verifier/report wedge.

## Positioning

- Product: a local reproducibility lab for open feed recommendation repos, starting with `xai-org/x-algorithm`.
- Primary audience: AI engineers, recommender-system builders, technical creators, and teams evaluating feed ranking architectures.
- Promise: generate a pinned local report that verifies source, artifacts, runnable paths, and architecture boundaries.
- Avoid: "beat the X algorithm", reach guarantees, scraping private feeds, or claims that public source fully explains live platform behavior.
- Commodity warning: generic algorithm-explainer skills are easy to copy. Keep the wedge on runnable evidence, commit pins, artifact checks, and generated files.

## First Free MVP

Ship the verifier/report flow free for 30 to 45 days.

Outputs:

- `run_report.md`
- `artifact_check.md`
- `architecture_map.html`
- `manifest.json`

First 10 users:

- People publicly discussing `xai-org/x-algorithm`
- Recsys engineers in public developer communities
- Codex, Claude Code, Cursor, and OpenClaw users who want a reproducible demo artifact

First 100 touches:

- 20 direct replies to public discussions about `xai-org/x-algorithm`, Phoenix, Grok-derived recommendation systems, or open recommender repos
- 20 short demo posts with generated report screenshots
- 20 targeted messages to opted-in dev peers
- 20 posts/comments in recsys or AI engineering communities, with the report output shown
- 20 follow-ups with people who publicly discussed similar repos or asked for runnable examples

## Share Trigger

- user feels: relief that the famous repo is locally mapped and not just bookmarked
- user has: a commit-pinned report and architecture map
- user shares with: AI/recsys/dev-tool peers
- user says: "I verified the open X For You algorithm locally at commit `<sha>`; here is the report."
- user gains: status as someone who ran and understood the release, not just repeated a thread

## Metrics

- Day 7: 10 successful local report generations, 3 public shares
- Day 30: 30 generated reports, 8 shares, 3 requests for custom corpus/app adaptation
- Day 60: 2 paid pilots or park paid work
- Shutdown threshold: fewer than 10 real runs or zero shares by day 30

## Paid Upgrade Candidates

Only expand after inbound demand:

- custom corpus adapter for Phoenix-like demos
- recommender pipeline scaffold for a user's own app
- internal engineering explainer/training deck
- recurring repo change monitor with practical impact summaries

Do not charge for the first report generator. Charge only for adaptation work or recurring analysis after users ask for it.

## Safety Boundaries

- Use public source and user-owned data only.
- Do not scrape private X feeds, DMs, hidden communities, or account-only analytics.
- Do not store credentials, cookies, API keys, or session exports.
- Do not promise revenue, reach, ranking, virality, health, legal, financial, or educational outcomes.
- State that public code may not fully match live production behavior.
