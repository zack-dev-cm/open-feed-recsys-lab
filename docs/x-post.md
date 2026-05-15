# X Post Drafts

## Short

I built Open Feed Recsys Lab: Codex/ClawHub skills for `xai-org/x-algorithm`.

It now covers reproducibility reports, viral claim audits, and TinyTroupe-inspired synthetic audience pretests for draft posts.

Repo: https://github.com/zack-dev-cm/open-feed-recsys-lab

## Thread

1/ I built Open Feed Recsys Lab for the newly updated open X For You algorithm repo.

The goal is not "beat the algorithm." It is reproducibility: what source did you inspect, what artifacts exist, and what can you honestly claim was run?

2/ The first skill generates:

- `run_report.md`
- `artifact_check.md`
- `architecture_map.html`
- `manifest.json`

It starts with `xai-org/x-algorithm` and pins the inspected commit.

3/ A lightweight clone is source-inspectable, but Phoenix inference needs the official Git LFS artifact extracted first.

The lab makes that boundary explicit instead of pretending that `git clone` equals a full model run.

4/ On the current open repo, the report also catches doc drift:

Root README and `phoenix/README.md` disagree on mini-model `emb_size` and `num_layers`.

That is exactly the kind of thing a reproducibility report should surface.

5/ I added two companion paths:

- audit viral claims against public files
- compare draft posts with synthetic personas before you publish

Both keep the same boundary: no reach prediction, no shadowban diagnosis, no live For You clone.

6/ Use it with Codex, Claude Code, or ClawHub when you want a concrete local artifact before writing takes about the open algorithm.

Repo:
https://github.com/zack-dev-cm/open-feed-recsys-lab

## Alt CTA

If you starred `xai-org/x-algorithm` but have not run, mapped, audited, or drafted around it yet, this gives you a clean first artifact in one command.
