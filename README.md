# Open Feed Recsys Lab

Generate commit-pinned reproducibility reports and source-backed claim audits for open feed recommendation repositories, starting with [`xai-org/x-algorithm`](https://github.com/xai-org/x-algorithm).

The repo includes two Codex/ClawHub skills:

- `open-feed-recsys-lab`: produces local reproducibility reports.
- `x-algo-claim-auditor`: audits viral X algorithm claims against public source.

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

Canonical tutorial: https://zack-dev-cm.github.io/open-feed-recsys-lab/

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

## Install As A Codex Skill

Copy or symlink `skill/open-feed-recsys-lab` into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skill/open-feed-recsys-lab "${CODEX_HOME:-$HOME/.codex}/skills/open-feed-recsys-lab"
cp -R skill/x-algo-claim-auditor "${CODEX_HOME:-$HOME/.codex}/skills/x-algo-claim-auditor"
```

## Install From ClawHub

```bash
clawhub install open-feed-recsys-lab
```

## Boundary

This is not an "algorithm growth hack" and does not promise reach, ranking, virality, revenue, or live-platform equivalence. It uses public source and user-owned local files only.

## Development

```bash
python3 -m unittest discover -s tests
python3 scripts/check_skill_bundle.py
python3 -m py_compile skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py
```

## License

MIT-0
