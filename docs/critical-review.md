# Critical Review

## Verdict

Ship both skills free as a two-step proof system:

- `open-feed-recsys-lab`: reproducibility report for the public repo.
- `x-algo-claim-auditor`: source-backed verdicts for viral claims.

Do not expand either skill into creator-growth prediction, shadowban diagnosis, or account-specific feed analysis.

## What Improved

- The original skill stayed narrow: reports, artifact readiness, architecture maps, and doc drift.
- The new auditor absorbs the viral "is this claim true?" demand without polluting the reproducibility workflow.
- The auditor emits a concrete share artifact: `claim_audit.md`, `claim_audit.json`, `share_card.md`, and `share_card.svg`.
- Claim outputs use bounded verdicts: `supported`, `misleading`, `unsupported`, and `not_public_repo`.
- The default high-risk claim, "replies are worth 150x a like," is handled as `misleading`, not as a growth promise.
- Both skills avoid private X data, cookies, account analytics, DMs, and live feed scraping.

## Remaining Weaknesses

- `x-algo-claim-auditor` is heuristic and keyword/rule based; it is not a formal semantic verifier.
- The auditor does not yet run OCR itself. Screenshot text must be pasted or extracted by the calling agent.
- Evidence line numbers are tied to the checked-out source revision and can drift as the upstream repo changes.
- The auditor can miss claims that use vague wording, memes, or screenshots with little text.
- Phoenix execution still requires the official ~3.12 GB Git LFS artifact; this path is smoke-tested for readiness, not fully executed in CI.
- ClawHub/static scanners may flag subprocess/network use. The use is intentional: local git/source inspection and optional clone operations.
- The first traffic source still depends on public reply work by the operator.

## Product Gate

| Product | Pain | Trust | Share | Traffic | Free MVP | Paid path | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `open-feed-recsys-lab` | 2 | 2 | 2 | 1 | 2 | 1 | Ship Free |
| `x-algo-claim-auditor` | 2 | 2 | 2 | 2 | 2 | 1 | Ship Free |

## Kill Boundaries

- Kill or park any feature that claims exact reach prediction.
- Kill any workflow requiring private account cookies, logged-in X analytics, DMs, or hidden feed data.
- Park monetization until there are at least 20 public shares or 5 repeat users.
- Park screenshot-first UX until OCR quality is tested on real public screenshots.

## Smallest Next Experiments

For `open-feed-recsys-lab`:

> I verified the open X For You algorithm repo locally at commit `e414c17`. Phoenix is source-inspectable, but execution is blocked until the 3.12 GB LFS artifact is extracted.

Day 7 target: 10 generated reports and 3 public shares.

For `x-algo-claim-auditor`:

> Send me a viral X algorithm claim. I will return a public-source verdict with file citations.

Day 7 target: 20 audited claims, 5 public share cards, and 3 claims submitted by people other than the builder.
