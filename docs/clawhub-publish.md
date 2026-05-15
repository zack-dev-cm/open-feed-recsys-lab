# ClawHub Publish Notes

## Published Skills

| Skill | Version | Source path | Tags |
| --- | --- | --- | --- |
| `open-feed-recsys-lab` | `1.0.2` | `skill/open-feed-recsys-lab` | `recsys,x-algorithm,phoenix,codex` |
| `x-algo-claim-auditor` | `1.0.0` | `skill/x-algo-claim-auditor` | `x-algorithm,claims,recsys,codex` |
| `tinytroupe-feed-research-lab` | `1.0.0` | `skill/tinytroupe-feed-research-lab` | `tinytroupe,synthetic-audience,recsys,codex` |

## Publish Commands

```bash
clawhub publish /Users/zack/Documents/GitHub/open-feed-recsys-lab/skill/open-feed-recsys-lab \
  --slug open-feed-recsys-lab \
  --name "Open Feed Recsys Lab" \
  --version 1.0.2 \
  --tags "recsys,x-algorithm,phoenix,codex" \
  --changelog "Add companion claim-auditor routing guidance while preserving the reproducibility report workflow."
```

```bash
clawhub publish /Users/zack/Documents/GitHub/open-feed-recsys-lab/skill/x-algo-claim-auditor \
  --slug x-algo-claim-auditor \
  --name "X Algo Claim Auditor" \
  --version 1.0.0 \
  --tags "x-algorithm,claims,recsys,codex" \
  --changelog "Initial release: audit viral X algorithm claims against public source with verdicts, evidence ledgers, and share cards."
```

```bash
clawhub publish /Users/zack/Documents/GitHub/open-feed-recsys-lab/skill/tinytroupe-feed-research-lab \
  --slug tinytroupe-feed-research-lab \
  --name "TinyTroupe Feed Research Lab" \
  --version 1.0.0 \
  --tags "tinytroupe,synthetic-audience,recsys,codex" \
  --changelog "Initial release: compare draft posts with deterministic synthetic audience personas and bounded feed-research reports."
```

## Install Smoke

```bash
rm -rf /tmp/clawhub-skill-install-smoke
mkdir -p /tmp/clawhub-skill-install-smoke
clawhub --workdir /tmp/clawhub-skill-install-smoke --dir skills install open-feed-recsys-lab
clawhub --workdir /tmp/clawhub-skill-install-smoke --dir skills install x-algo-claim-auditor
clawhub --workdir /tmp/clawhub-skill-install-smoke --dir skills install tinytroupe-feed-research-lab
```

## Expected Static Review Notes

The source-inspection skills intentionally use local subprocess calls for `git`, Python checks, or local source inspection. The claim auditor may clone the public `xai-org/x-algorithm` repo when no `--repo-dir` is supplied.

The skills do not ask for cookies, tokens, credentials, private X data, account analytics, private feeds, DMs, or private messages. They should not be represented as reach predictors, shadowban detectors, growth hacks, or live For You feed clones. The TinyTroupe-inspired skill is a deterministic pretest and optional experiment bridge, not Microsoft TinyTroupe itself.
