---
name: x-algo-claim-auditor
description: Audit public claims about xai-org/x-algorithm, the X For You algorithm, Phoenix, Grox, Home Mixer, engagement weights, filters, ads blending, or "test my post before publishing" narratives. Use when Codex needs to turn a pasted claim, screenshot text, thread summary, or public post claim into a source-backed verdict with file citations, evidence ledger, and shareable claim card while avoiding reach-prediction or private-account claims.
license: MIT-0
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/open-feed-recsys-lab","skillKey":"x-algo-claim-auditor","requires":{"anyBins":["python3","python"],"anyTools":["git"]}}}
---

# X Algo Claim Auditor

Use this skill to audit viral or product claims against the public `xai-org/x-algorithm` source. The goal is a defensible proof artifact, not growth advice.

## Core Workflow

1. Extract the exact claim from the user, screenshot OCR, public post, or pasted text.
2. Run `scripts/x_algo_claim_auditor.py` with the claim and a local or cloned `x-algorithm` checkout.
3. Read `claim_audit.md` and `claim_audit.json`.
4. Answer with the verdict, strongest evidence, and boundary: what the public repo proves and what it does not prove.
5. If the user wants a share artifact, use `share_card.md` or `share_card.svg`.

## Quick Start

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/x-algo-claim-auditor"
python3 "$SKILL_DIR/scripts/x_algo_claim_auditor.py" \
  --claim "Replies are worth 150x a like in the new X algorithm" \
  --output-dir /tmp/x-algo-claim-audit
```

Use an existing checkout:

```bash
python3 "$SKILL_DIR/scripts/x_algo_claim_auditor.py" \
  --claim-file /tmp/claim.txt \
  --repo-dir /path/to/x-algorithm \
  --output-dir /tmp/x-algo-claim-audit
```

The script writes:

- `claim_audit.md`: human-readable verdict and evidence.
- `claim_audit.json`: machine-readable ledger.
- `share_card.md`: short public-safe card.
- `share_card.svg`: image-style claim card for screenshots.

## Verdict Meanings

- `supported`: the public repo directly supports the narrow claim.
- `misleading`: the repo supports a weaker statement, but the claim overstates precision, production equivalence, or causality.
- `unsupported`: no public source evidence was found for the claim.
- `not_public_repo`: the claim depends on production configs, private thresholds, account state, or live ranking behavior absent from the repo.

## Boundaries

Read `references/claim-boundaries.md` when the user asks about reach prediction, shadowbans, hidden boosts, private configs, or account-specific feed behavior.

Never claim:

- the public repo is the full live production system,
- a draft post can be scored exactly before publishing,
- a user is shadowbanned or boosted,
- exact engagement multipliers exist unless public source lines show them,
- private X account analytics, feed state, cookies, or DMs should be scraped.

## Agent-Specific Use

For Codex: prefer local source inspection and the deterministic script. Cite file paths and line numbers from the ledger.

For Claude: use the ledger to write longer explanations or threads, but keep claims tied to public source evidence.

For OpenClaw: only use browser automation for public pages, screenshots, or user-approved publishing of generated cards. Pause for login, CAPTCHA, passkey, or private account pages.
