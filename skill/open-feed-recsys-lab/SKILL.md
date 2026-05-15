---
name: open-feed-recsys-lab
description: Generate reproducible local reports for open feed recommendation repositories, especially xai-org/x-algorithm. Use when the user asks to analyze, verify, run, map, explain, package, monitor, or build Codex/Claude/OpenClaw workflows around the X For You algorithm, Phoenix retrieval/ranking, Home Mixer, Thunder, Grox, ads blending, recommender-system pipeline scaffolds, or shareable architecture/run artifacts.
license: MIT-0
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/open-feed-recsys-lab","skillKey":"open-feed-recsys-lab","requires":{"anyBins":["python3","python"],"anyTools":["git"]}}}
---

# Open Feed Recsys Lab

Use this skill to turn a high-attention feed recommendation repo into a concrete local artifact: source checkout, artifact readiness check, architecture map, and reproducibility report.

Default target: `https://github.com/xai-org/x-algorithm`.

## Core Workflow

1. Generate the local lab report with `scripts/open_feed_recsys_lab.py`.
2. Inspect the generated `run_report.md`, `artifact_check.md`, and `architecture_map.html`.
3. If Phoenix artifacts are missing, explain the LFS blocker and do not pretend the model was run.
4. If the user asks for a launch/product angle, read `references/product-gate.md` and keep the free MVP narrow.
5. If the user asks to adapt the architecture, use the report as the source of truth and scaffold only the requested slice.

## Quick Start

Run from the user's chosen workspace:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/open-feed-recsys-lab"
python3 "$SKILL_DIR/scripts/open_feed_recsys_lab.py"
```

This creates:

- `open-feed-recsys-lab-report/run_report.md`
- `open-feed-recsys-lab-report/artifact_check.md`
- `open-feed-recsys-lab-report/architecture_map.html`
- `open-feed-recsys-lab-report/manifest.json`

The script clones with `GIT_LFS_SKIP_SMUDGE=1` by default through the environment, so the report can be produced without pulling multi-GB model artifacts.

## Existing Clone

Use an existing checkout when available:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/open-feed-recsys-lab"
python3 "$SKILL_DIR/scripts/open_feed_recsys_lab.py" \
  --repo-dir /path/to/x-algorithm \
  --output-dir /path/to/report
```

Use `--force-clone` only when it is safe to delete and recreate the script-managed clone directory.
If `--repo-dir` points to an existing checkout, the script reports the current checkout and warns when it does not obviously match `--ref`; it does not silently reset user work.

## Phoenix Execution

Only run Phoenix after extracted artifacts are present. The expected extracted directory is:

```text
phoenix/artifacts/oss-phoenix-artifacts/
```

Expected files include:

- `retrieval/model_params.npz`
- `retrieval/embedding_tables.npz`
- `retrieval/config.json`
- `ranker/model_params.npz`
- `ranker/embedding_tables.npz`
- `ranker/config.json`
- `sports_corpus.npz`
- `example_sequence.json`

When artifacts are ready:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/open-feed-recsys-lab"
python3 "$SKILL_DIR/scripts/open_feed_recsys_lab.py" \
  --repo-dir /path/to/x-algorithm \
  --artifacts-dir /path/to/oss-phoenix-artifacts \
  --run-phoenix
```

Use `--run-pytest` only when `uv` and dependencies are available.

## Report Interpretation

Treat the generated reports as evidence, not marketing copy.

- `run_report.md`: repo metadata, component inventory, doc checks, command outputs.
- `artifact_check.md`: Git LFS pointer size, extracted artifact completeness, doc/config mismatches.
- `architecture_map.html`: shareable standalone map of Home Mixer, Phoenix, Thunder, Grox, and Candidate Pipeline.
- `manifest.json`: machine-readable source for follow-up tooling.

If the report says Phoenix is not run-ready, state that source inspection succeeded but execution is blocked by missing extracted LFS artifacts.

## Agent-Specific Use

For Codex:

- Prefer local source inspection, patches, and reproducible report generation.
- Use the generated manifest to drive follow-up scripts or scaffolds.

For Claude or Claude Code:

- Provide the report files as context for long-form architecture explanations.
- Keep claims tied to file paths, commit IDs, and artifact readiness.

For OpenClaw:

- Use browser automation only for public pages, public screenshots, or user-approved publishing of generated artifacts.
- Do not scrape private X feeds, private analytics, DMs, cookies, or account-only pages.

## Product Boundary

Do not position this as an "algorithm growth hack" or a way to guarantee reach. The first shareable win is reproducibility:

```text
I verified the open X For You algorithm locally at commit <sha>; here is the report.
```

When evaluating whether to expand the product, read `references/product-gate.md`.
