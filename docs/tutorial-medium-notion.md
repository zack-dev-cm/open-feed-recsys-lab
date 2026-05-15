# How To Verify The Open X For You Algorithm Repo Locally

This tutorial is written for Medium or Notion. It shows how to turn `xai-org/x-algorithm` into a reproducible local report, audit viral algorithm claims, and pretest draft posts without pretending that a source checkout automatically runs the full model or predicts reach.

## The Problem

The open X For You algorithm repository is useful, but it has two different surfaces:

- source code you can inspect immediately,
- Phoenix model artifacts that require a large Git LFS archive before inference can run.

That difference matters. If you only clone the repo, you can map the architecture and inspect the source. You cannot honestly claim you ran Phoenix unless the artifacts are downloaded and extracted.

## What The Lab Produces

Open Feed Recsys Lab generates four files:

- `run_report.md`: commit, repo status, component inventory, warnings, and optional command outputs
- `artifact_check.md`: LFS pointer, expected Phoenix files, and missing artifacts
- `architecture_map.html`: shareable map of Home Mixer, Phoenix, Thunder, Grox, and Candidate Pipeline
- `manifest.json`: machine-readable facts for follow-up tooling

The companion claim auditor generates source-backed verdicts for viral claims, and the TinyTroupe-inspired feed research skill compares draft posts with synthetic personas. Those outputs are useful for public explanation and drafting, but they are not live X ranking predictions.

## Install

Clone the lab:

```bash
git clone https://github.com/zack-dev-cm/open-feed-recsys-lab
cd open-feed-recsys-lab
```

Run the report generator:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py
```

By default, the script clones `xai-org/x-algorithm` with Git LFS smudge disabled. That keeps the first report lightweight and avoids pulling multi-GB artifacts unexpectedly.

## Use An Existing Checkout

If you already cloned the X algorithm repo:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --repo-dir /path/to/x-algorithm \
  --output-dir /tmp/open-feed-recsys-lab-report
```

Pin a specific commit:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --ref e414c17 \
  --output-dir /tmp/open-feed-recsys-lab-report
```

## Read The Result

Open `run_report.md` first.

The report tells you:

- which commit was inspected,
- whether the working tree was clean,
- whether key components are present,
- whether Phoenix artifacts are complete,
- whether documentation and extracted configs agree.

Then open `artifact_check.md`.

For a lightweight clone, expect the Phoenix zip to be a Git LFS pointer. That means source inspection is valid, but Phoenix execution is not ready yet.

Finally, open `architecture_map.html`.

This is the shareable artifact: it maps the request flow across Home Mixer, Thunder, Phoenix, ads/prompts/who-to-follow, hydration/filtering/scoring, and the ranked feed response.

## Run Phoenix Only When Artifacts Exist

After downloading and extracting the official artifact, point the lab at the extracted folder:

```bash
python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py \
  --repo-dir /path/to/x-algorithm \
  --artifacts-dir /path/to/oss-phoenix-artifacts \
  --run-phoenix
```

The expected extracted files include retrieval and ranker configs, model params, embedding tables, the sports corpus, and the example sequence.

## Audit A Viral Claim

Use the claim auditor when a post says something like "replies are worth 150x a like" or "Premium gets a visibility boost":

```bash
python3 skill/x-algo-claim-auditor/scripts/x_algo_claim_auditor.py \
  --repo-dir /path/to/x-algorithm \
  --claim "Replies are worth 150x a like in the new X algorithm" \
  --output-dir /tmp/x-algo-claim-audit
```

The output is a verdict, evidence ledger, and share card. It should say `misleading` when the public source supports engagement probabilities or weights in general but not the exact viral multiplier.

## Pretest Draft Posts

Use the TinyTroupe-inspired research skill when you have multiple drafts and want a bounded synthetic audience read:

```bash
python3 skill/tinytroupe-feed-research-lab/scripts/tinytroupe_feed_research_lab.py \
  --audience "AI builders and creator-operators interested in source-backed algorithm research" \
  --draft "I audited a viral X algorithm claim against public source. Verdict: misleading. What should I check next?" \
  --draft "Replies are king. Here is what the public repo actually proves." \
  --output-dir /tmp/tinytroupe-feed-research
```

Read `feed_research_report.md` for the best synthetic conversation draft, objections, and rewrite suggestions. Keep the footer attached: this is synthetic audience research, not reach, ranking, virality, revenue, or live production behavior.

## What This Does Not Prove

This does not prove that the public repo fully matches live production behavior. It also does not predict reach, virality, creator growth, or account performance.

It proves something narrower and more useful:

- what source was inspected,
- what artifacts are present,
- whether the local Phoenix run is ready,
- where the public docs and configs agree or disagree.
- whether a viral claim is supported by public files,
- how synthetic personas react to a draft under explicit boundaries.

## Share Prompt

Use this only after generating your own report:

```text
I verified the open X For You algorithm repo locally at commit <sha>. Here is the report: source inspected, Phoenix artifact readiness checked, and architecture mapped.
```

## Next Step

Use the generated `manifest.json` to build custom architecture docs, runbooks, or recommender-system scaffolds for your own app.
