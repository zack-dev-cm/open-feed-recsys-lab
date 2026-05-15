# Open Feed Recsys Lab

Generate commit-pinned reproducibility reports, source-backed claim audits, and bounded synthetic audience research for open feed recommendation repositories, starting with [`xai-org/x-algorithm`](https://github.com/xai-org/x-algorithm).

The repo includes three Codex/ClawHub skills:

- `open-feed-recsys-lab`: produces local reproducibility reports.
- `x-algo-claim-auditor`: audits viral X algorithm claims against public source.
- `tinytroupe-feed-research-lab`: compares draft posts with synthetic audience personas for qualitative pretesting.

`open-feed-recsys-lab` produces four local artifacts:

- `run_report.md`: source, commit, component, warning, and command-check summary
- `artifact_check.md`: Git LFS and Phoenix artifact readiness checks
- `architecture_map.html`: standalone architecture map for sharing or review
- `manifest.json`: machine-readable report data

`x-algo-claim-auditor` produces four claim-audit artifacts:

- `claim_audit.md`: human-readable verdict and evidence ledger
- `claim_audit.json`: machine-readable claim, verdict, confidence, and citations
- `share_card.md`: short public-safe share card text
- `share_card.svg`: visual share card for screenshots or posts

`tinytroupe-feed-research-lab` produces six synthetic research artifacts:

- `feed_research_report.md`: draft comparison, best draft, objections, and rewrite guidance
- `feed_research.json`: machine-readable drafts, personas, reactions, warnings, and scores
- `persona_reactions.csv`: persona-by-draft reaction rows
- `share_card.md`: short public-safe summary
- `share_card.svg`: visual summary card
- `tinytroupe_experiment_plan.md`: bridge plan for a later TinyTroupe run

Canonical tutorial: https://zack-dev-cm.github.io/open-feed-recsys-lab/tutorial.html

## Why

The X For You algorithm repo is high-interest, but a lightweight clone does not automatically mean the Phoenix demo can run. The lab makes that explicit: it verifies source state, flags missing extracted LFS artifacts, and catches documentation/config mismatches before anyone overclaims what was reproduced.

## Quick Start

Run the reproducibility report script directly:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py
```

Use an existing checkout:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --repo-dir /path/to/x-algorithm \
  --output-dir /tmp/open-feed-recsys-lab-report
```

Pin a commit or ref:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --ref e414c17 \
  --output-dir /tmp/open-feed-recsys-lab-report
```

Run Phoenix only after the official LFS artifact is downloaded and extracted:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --repo-dir /path/to/x-algorithm \
  --artifacts-dir /path/to/oss-phoenix-artifacts \
  --run-phoenix
```

Audit a viral claim against the public repo:

```bash
python3 skill/x-algo-claim-auditor/scripts/x_algo_claim_auditor.py \
  --repo-dir /path/to/x-algorithm \
  --claim "Replies are worth 150x a like in the new X algorithm" \
  --output-dir /tmp/x-algo-claim-audit
```

Compare draft posts with synthetic audience personas:

```bash
python3 skill/tinytroupe-feed-research-lab/scripts/tinytroupe_feed_research_lab.py \
  --audience "AI builders and creator-operators interested in source-backed algorithm research" \
  --draft "I audited a viral X algorithm claim against public source. Verdict: misleading. What should I check next?" \
  --draft "Replies are king. Here is what the public repo actually proves." \
  --output-dir /tmp/tinytroupe-feed-research
```

## Install As A Codex Skill

Copy or symlink `skill/open-feed-recsys-lab` into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skill/open-feed-recsys-lab "${CODEX_HOME:-$HOME/.codex}/skills/open-feed-recsys-lab"
cp -R skill/x-algo-claim-auditor "${CODEX_HOME:-$HOME/.codex}/skills/x-algo-claim-auditor"
cp -R skill/tinytroupe-feed-research-lab "${CODEX_HOME:-$HOME/.codex}/skills/tinytroupe-feed-research-lab"
```

## Install From ClawHub

```bash
clawhub install open-feed-recsys-lab
clawhub install x-algo-claim-auditor
clawhub install tinytroupe-feed-research-lab
```

## Boundary

This is not an "algorithm growth hack" and does not promise reach, ranking, virality, revenue, or live-platform equivalence. The synthetic audience skill is qualitative draft research, not a TinyTroupe replacement, live X clone, shadowban detector, or prediction system. The repo uses public source and user-owned local files only.

## Development

```bash
python3 -m unittest discover -s tests
python3 scripts/check_skill_bundle.py
python3 -m py_compile \
  skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  skill/x-algo-claim-auditor/scripts/x_algo_claim_auditor.py \
  skill/tinytroupe-feed-research-lab/scripts/tinytroupe_feed_research_lab.py
```

## License

MIT-0
