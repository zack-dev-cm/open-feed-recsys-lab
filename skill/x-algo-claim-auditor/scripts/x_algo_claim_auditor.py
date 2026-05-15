#!/usr/bin/env python3
"""Audit public X algorithm claims against xai-org/x-algorithm source."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_REPO = "https://github.com/xai-org/x-algorithm"
DEFAULT_WORK_DIR = ".x-algo-claim-auditor"
MAX_EVIDENCE_PER_RULE = 8


@dataclass
class Evidence:
    rule: str
    file: str
    line: int
    match: str
    why: str


@dataclass
class Rule:
    name: str
    triggers: tuple[str, ...]
    files: tuple[str, ...]
    patterns: tuple[str, ...]
    proves: str


RULES: tuple[Rule, ...] = (
    Rule(
        name="action_weights",
        triggers=(
            "reply",
            "replies",
            "like",
            "likes",
            "favorite",
            "repost",
            "retweet",
            "bookmark",
            "share",
            "dwell",
            "weight",
            "multiplier",
            "score",
            "engagement",
        ),
        files=(
            "home-mixer/scorers/ranking_scorer.rs",
            "home-mixer/scorers/weighted_scorer.rs",
            "home-mixer/side_effects/scored_stats_side_effect.rs",
            "README.md",
        ),
        patterns=(
            "FavoriteWeight",
            "ReplyWeight",
            "RetweetWeight",
            "ShareWeight",
            "DwellWeight",
            "NotInterestedWeight",
            "BlockAuthorWeight",
            "MuteAuthorWeight",
            "ReportWeight",
            "compute_weighted_score",
            "Weighted Scorer",
            "Final Score",
            "P(reply)",
            "P(repost)",
        ),
        proves="The public source includes action-probability scoring and configurable weights.",
    ),
    Rule(
        name="phoenix_architecture",
        triggers=(
            "phoenix",
            "transformer",
            "candidate isolation",
            "two tower",
            "two-tower",
            "retrieval",
            "ranking",
            "multi-action",
            "multi action",
            "grok",
        ),
        files=(
            "README.md",
            "phoenix/README.md",
            "phoenix/recsys_model.py",
            "phoenix/recsys_retrieval_model.py",
            "phoenix/run_pipeline.py",
        ),
        patterns=(
            "Retrieval",
            "Ranking",
            "Transformer",
            "candidate isolation",
            "candidates cannot attend",
            "multi-action",
            "multiple engagement",
            "run_pipeline",
            "sports_corpus",
            "oss-phoenix-artifacts",
        ),
        proves="The public source describes Phoenix retrieval/ranking and candidate isolation.",
    ),
    Rule(
        name="grox_content_understanding",
        triggers=(
            "grox",
            "spam",
            "safety",
            "ptos",
            "reply ranking",
            "banger",
            "content understanding",
            "classifier",
            "embedding",
        ),
        files=(
            "README.md",
            "grox/engine.py",
            "grox/dispatcher.py",
            "grox/classifiers/content/banger_initial_screen.py",
            "grox/classifiers/content/reply_ranking.py",
            "grox/classifiers/content/spam.py",
            "grox/classifiers/content/safety_ptos.py",
            "grox/tasks/task_spam_detection.py",
            "grox/tasks/task_rank_replies.py",
            "grox/tasks/task_post_safety_screen_deluxe.py",
        ),
        patterns=(
            "Grox",
            "content understanding",
            "BangerInitialScreen",
            "ReplyScorer",
            "spam",
            "safety",
            "PTOS",
            "ranked_replies",
            "embedding",
        ),
        proves="The public source includes Grox content-understanding and safety/reply-ranking surfaces.",
    ),
    Rule(
        name="filters_visibility",
        triggers=(
            "filter",
            "filters",
            "blocked",
            "muted",
            "mute",
            "visibility",
            "vf",
            "diversity",
            "author diversity",
            "buried",
            "kneecap",
            "shadow",
        ),
        files=(
            "README.md",
            "home-mixer/filters/author_socialgraph_filter.rs",
            "home-mixer/filters/muted_keyword_filter.rs",
            "home-mixer/filters/vf_filter.rs",
            "home-mixer/filters/previously_seen_posts_filter.rs",
            "home-mixer/filters/previously_served_posts_filter.rs",
            "home-mixer/filters/topic_ids_filter.rs",
            "home-mixer/scorers/author_diversity_scorer.rs",
            "home-mixer/scorers/ranking_scorer.rs",
        ),
        patterns=(
            "AuthorSocialgraphFilter",
            "MutedKeywordFilter",
            "VFFilter",
            "PreviouslySeenPostsFilter",
            "PreviouslyServedPostsFilter",
            "TopicFiltering",
            "AuthorDiversity",
            "diversity_multiplier",
            "blocked_user_ids",
            "muted_user_ids",
        ),
        proves="The public source includes multiple eligibility, visibility, history, topic, and diversity mechanisms.",
    ),
    Rule(
        name="ads_brand_safety",
        triggers=("ad", "ads", "brand safety", "brand-safety", "sponsored", "safe gap"),
        files=(
            "README.md",
            "home-mixer/ads/safe_gap_blender.rs",
            "home-mixer/ads/partition_organic_blender.rs",
            "home-mixer/ads/util.rs",
            "home-mixer/sources/ads_source.rs",
            "home-mixer/candidate_hydrators/ads_brand_safety_hydrator.rs",
            "home-mixer/candidate_hydrators/ads_brand_safety_vf_hydrator.rs",
            "home-mixer/selectors/blender_selector.rs",
        ),
        patterns=(
            "AdsSource",
            "SafeGap",
            "brand safety",
            "BrandSafety",
            "AdIndex",
            "blend",
            "ads",
        ),
        proves="The public source includes ads source, blending, and brand-safety-related code.",
    ),
    Rule(
        name="local_repro_boundary",
        triggers=(
            "clone",
            "locally",
            "local",
            "test my post",
            "before publishing",
            "preflight",
            "simulate",
            "run pipeline",
            "lfs",
            "artifact",
        ),
        files=(
            "README.md",
            "phoenix/README.md",
            "phoenix/run_pipeline.py",
            "phoenix/artifacts/oss-phoenix-artifacts.zip",
        ),
        patterns=(
            "run_pipeline",
            "Git LFS",
            "oss-phoenix-artifacts",
            "sports_corpus",
            "example_sequence",
            "frozen checkpoint",
            "mini version",
            "out-of-the-box inference",
        ),
        proves="The public repo supports local source inspection and demo Phoenix execution after artifacts are extracted.",
    ),
)


STOPWORDS = {
    "about",
    "after",
    "again",
    "algorithm",
    "because",
    "before",
    "being",
    "claim",
    "could",
    "every",
    "from",
    "have",
    "into",
    "just",
    "more",
    "much",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "with",
    "would",
    "your",
}


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def ensure_repo(args: argparse.Namespace) -> Path:
    if args.repo_dir:
        repo = Path(args.repo_dir).expanduser().resolve()
        if not (repo / ".git").exists() and not (repo / "README.md").exists():
            raise SystemExit(f"--repo-dir does not look like x-algorithm: {repo}")
        return repo

    work_dir = Path(args.work_dir).expanduser().resolve()
    repo = work_dir / "x-algorithm"
    if args.force_clone and repo.exists():
        shutil.rmtree(repo)
    if not repo.exists():
        work_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        run(["git", "clone", "--depth", "1", "--filter=blob:none", DEFAULT_REPO, str(repo)], env=env)
    if args.ref and args.ref != "main":
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=repo)
        run(["git", "checkout", "FETCH_HEAD"], cwd=repo)
    return repo


def repo_metadata(repo: Path) -> dict[str, str | None]:
    def maybe(cmd: list[str]) -> str | None:
        try:
            return run(cmd, cwd=repo)
        except Exception:
            return None

    return {
        "path": str(repo),
        "remote": maybe(["git", "config", "--get", "remote.origin.url"]),
        "commit": maybe(["git", "rev-parse", "HEAD"]),
        "short_commit": maybe(["git", "rev-parse", "--short", "HEAD"]),
        "status": maybe(["git", "status", "--short"]),
    }


def compile_pattern(pattern: str) -> re.Pattern[str]:
    if pattern.startswith("re:"):
        return re.compile(pattern[3:], re.IGNORECASE)
    return re.compile(re.escape(pattern), re.IGNORECASE)


def search_file(repo: Path, rel: str, patterns: Iterable[str], rule: Rule) -> list[Evidence]:
    path = repo / rel
    if not path.exists() or not path.is_file():
        return []
    compiled = [compile_pattern(pattern) for pattern in patterns]
    evidence: list[Evidence] = []
    for lineno, line in enumerate(read_text(path).splitlines(), start=1):
        compact = " ".join(line.strip().split())
        if not compact:
            continue
        for regex in compiled:
            if regex.search(line):
                evidence.append(
                    Evidence(
                        rule=rule.name,
                        file=rel,
                        line=lineno,
                        match=compact[:240],
                        why=rule.proves,
                    )
                )
                break
        if len(evidence) >= MAX_EVIDENCE_PER_RULE:
            break
    return evidence


def triggered_rules(claim: str) -> list[Rule]:
    lowered = claim.lower()
    hits = []
    for rule in RULES:
        if any(trigger in lowered for trigger in rule.triggers):
            hits.append(rule)
    return hits


def fallback_terms(claim: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", claim.lower())
    terms = []
    for word in words:
        if word not in STOPWORDS and word not in terms:
            terms.append(word)
    return terms[:8]


def fallback_evidence(repo: Path, claim: str) -> list[Evidence]:
    terms = fallback_terms(claim)
    if not terms:
        return []
    pseudo_rule = Rule(
        name="keyword_fallback",
        triggers=(),
        files=(),
        patterns=(),
        proves="Related keyword evidence found, but it may not directly support the claim.",
    )
    evidence: list[Evidence] = []
    allowed_suffixes = {".md", ".rs", ".py", ".toml"}
    for path in sorted(repo.rglob("*")):
        if ".git" in path.parts or not path.is_file() or path.suffix not in allowed_suffixes:
            continue
        rel = str(path.relative_to(repo))
        try:
            lines = read_text(path).splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(term in lowered for term in terms):
                evidence.append(
                    Evidence(
                        rule=pseudo_rule.name,
                        file=rel,
                        line=lineno,
                        match=" ".join(line.strip().split())[:240],
                        why=pseudo_rule.proves,
                    )
                )
                break
        if len(evidence) >= 8:
            break
    return evidence


def collect_evidence(repo: Path, claim: str) -> tuple[list[Rule], list[Evidence]]:
    rules = triggered_rules(claim)
    evidence: list[Evidence] = []
    for rule in rules:
        rule_evidence: list[Evidence] = []
        for rel in rule.files:
            rule_evidence.extend(search_file(repo, rel, rule.patterns, rule))
            if len(rule_evidence) >= MAX_EVIDENCE_PER_RULE:
                break
        evidence.extend(rule_evidence[:MAX_EVIDENCE_PER_RULE])
    if not evidence:
        evidence.extend(fallback_evidence(repo, claim))
    return rules, evidence


def has_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def classify(claim: str, rules: list[Rule], evidence: list[Evidence]) -> dict[str, object]:
    text = claim.lower()
    rule_names = {rule.name for rule in rules}

    exact_number = bool(re.search(r"\b\d+(?:\.\d+)?\s*x\b", text))
    comparative_formula = bool(
        re.search(r"\brepl(?:y|ies)\b.{0,40}(?:>|\bworth\b|\bbeats?\b|\bking\b|\blikes?\b)", text)
    )

    if has_any(text, ("premium", "verified boost", "visibility boost", "followers dont matter", "followers don't matter")):
        return verdict(
            "unsupported",
            0.82,
            "The public repo evidence found by this auditor does not support the claimed account-class or Premium visibility effect.",
            ["Public source can be checked for ranking components and feature names."],
            ["It does not prove account-specific boosts, Premium boosts, or live production ranking policy."],
        )

    if has_any(text, ("shadowban", "shadow ban", "secret threshold", "secret thresholds", "private config", "private rust", "hidden in rust")):
        return verdict(
            "not_public_repo",
            0.78,
            "The claim depends on private production settings or hidden thresholds that are not established by the public repo alone.",
            ["Public source includes filters, scorers, and parameter names that can be inspected."],
            ["It does not publish enough private production config to prove the alleged hidden threshold or account treatment."],
        )

    if has_any(text, ("test my post", "before publishing", "clone the for you", "clone for you", "exactly reproduce", "predict reach")):
        return verdict(
            "misleading",
            0.86,
            "The public repo supports local inspection and demo execution, but not exact live-feed or draft-post reach prediction.",
            ["Phoenix can be run locally only after the public artifact archive is downloaded and extracted."],
            ["A local demo does not reproduce a user's live For You feed or guarantee post performance."],
        )

    if has_any(text, ("external links", "external link", "links get buried", "link gets buried")):
        return verdict(
            "unsupported",
            0.72,
            "This auditor did not find public-source support for a direct external-link burial claim.",
            ["Public source can show scoring, filtering, and content-understanding mechanisms."],
            ["It does not by itself prove a direct penalty for all external links."],
        )

    if has_any(text, ("no hardcoded multiplier", "no hardcoded multipliers", "abolished", "no heuristics", "all manual rules are gone")):
        return verdict(
            "misleading",
            0.84,
            "The claim overstates the repo. The public source still includes filter/scoring paths and configurable action weights.",
            ["The repo describes Grok/Phoenix model scoring and includes parameter-driven weighted scoring paths."],
            ["It does not prove that all heuristics, filters, or weighting mechanisms are absent from live production."],
        )

    if exact_number or comparative_formula or "bookmarks" in text or "bookmark" in text:
        return verdict(
            "misleading",
            0.88,
            "The public source supports weighted action scoring, but this claim states exact public multipliers or ordering that the repo evidence does not prove.",
            ["Ranking combines predicted action probabilities with configurable weights."],
            ["The public repo does not publish enough production parameter values to prove the exact multiplier or universal ordering."],
        )

    if "ads_brand_safety" in rule_names:
        return verdict(
            "supported",
            0.78,
            "The narrow claim about ads blending or brand-safety surfaces is supported by public source evidence.",
            ["The repo includes ads source, blending, logging, and brand-safety-related modules."],
            ["It does not prove live ad auction policy or every production brand-safety threshold."],
        )

    if "grox_content_understanding" in rule_names:
        return verdict(
            "supported",
            0.8,
            "The narrow claim about Grox content-understanding surfaces is supported by public source evidence.",
            ["The repo includes Grox classifiers/tasks for safety, spam, embeddings, banger screening, and reply ranking."],
            ["It does not prove exact live model weights, thresholds, or enforcement policy."],
        )

    if "phoenix_architecture" in rule_names:
        return verdict(
            "supported",
            0.82,
            "The narrow Phoenix architecture claim is supported by public source evidence.",
            ["The repo documents Phoenix retrieval, ranking, transformer candidate isolation, and multi-action outputs."],
            ["It does not prove live production equivalence for a specific user or post."],
        )

    if "filters_visibility" in rule_names:
        return verdict(
            "supported",
            0.72,
            "The public repo supports the existence of filtering and diversity mechanisms, but not account-specific suppression claims.",
            ["The repo includes filters for author social graph, muted keywords, visibility filtering, seen/served history, topics, and author diversity."],
            ["It does not prove any specific user's content was suppressed or boosted."],
        )

    if evidence:
        return verdict(
            "unsupported",
            0.58,
            "Related source evidence was found, but this auditor cannot tie it directly to the claim.",
            ["Some public files contain related terms."],
            ["The exact claim needs narrower wording or manual source review."],
        )

    return verdict(
        "unsupported",
        0.7,
        "No public-source evidence was found for the claim.",
        [],
        ["The claim is not established by the public x-algorithm repository evidence available to this audit."],
    )


def verdict(
    label: str,
    confidence: float,
    summary: str,
    proves: list[str],
    does_not_prove: list[str],
) -> dict[str, object]:
    return {
        "verdict": label,
        "confidence": confidence,
        "summary": summary,
        "public_repo_proves": proves,
        "public_repo_does_not_prove": does_not_prove,
    }


def markdown_table_row(values: Iterable[object]) -> str:
    cells = []
    for value in values:
        text = str(value).replace("\n", " ").replace("|", "\\|")
        cells.append(text)
    return "| " + " | ".join(cells) + " |"


def render_markdown(audit: dict[str, object]) -> str:
    evidence = audit["evidence"]
    lines = [
        "# X Algorithm Claim Audit",
        "",
        f"- Generated: `{audit['generated_at']}`",
        f"- Verdict: `{audit['verdict']}`",
        f"- Confidence: `{audit['confidence']}`",
        f"- Repo commit: `{audit['repo'].get('short_commit') or audit['repo'].get('commit') or 'unknown'}`",
        "",
        "## Claim",
        "",
        str(audit["claim"]),
        "",
        "## Summary",
        "",
        str(audit["summary"]),
        "",
        "## What The Public Repo Proves",
        "",
    ]
    proves = audit["public_repo_proves"]
    lines.extend([f"- {item}" for item in proves] if proves else ["- No direct support found."])
    lines.extend(["", "## What It Does Not Prove", ""])
    does_not = audit["public_repo_does_not_prove"]
    lines.extend([f"- {item}" for item in does_not] if does_not else ["- No extra boundary noted."])
    lines.extend(["", "## Evidence Ledger", ""])
    if evidence:
        lines.append(markdown_table_row(["Rule", "File", "Line", "Evidence"]))
        lines.append("| --- | --- | ---: | --- |")
        for item in evidence:
            lines.append(
                markdown_table_row(
                    [item["rule"], item["file"], item["line"], f"`{item['match']}`"]
                )
            )
    else:
        lines.append("No matching public-source evidence was found.")
    lines.extend(
        [
            "",
            "## Share Prompt",
            "",
            str(audit["share_prompt"]),
            "",
        ]
    )
    return "\n".join(lines)


def render_share_card_md(audit: dict[str, object]) -> str:
    return "\n".join(
        [
            f"Verdict: {str(audit['verdict']).upper()}",
            "",
            textwrap.fill(str(audit["summary"]), width=88),
            "",
            f"Claim: {audit['claim']}",
            "",
            f"Repo: xai-org/x-algorithm @ {audit['repo'].get('short_commit') or 'unknown'}",
        ]
    )


def svg_lines(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        wrapped = textwrap.wrap(paragraph, width=width) or [""]
        lines.extend(wrapped)
    return lines


def render_share_card_svg(audit: dict[str, object]) -> str:
    verdict_label = str(audit["verdict"]).upper()
    colors = {
        "SUPPORTED": "#0F7B4F",
        "MISLEADING": "#B45309",
        "UNSUPPORTED": "#9F1239",
        "NOT_PUBLIC_REPO": "#4338CA",
    }
    accent = colors.get(verdict_label, "#374151")
    claim = "Claim: " + str(audit["claim"])
    summary = str(audit["summary"])
    body_lines = svg_lines(summary, 72)[:5] + [""] + svg_lines(claim, 72)[:4]
    height = 210 + len(body_lines) * 25
    text_parts = []
    y = 142
    for line in body_lines:
        if line:
            text_parts.append(
                f'<text x="42" y="{y}" class="body">{html.escape(line)}</text>'
            )
        y += 25
    commit = audit["repo"].get("short_commit") or "unknown"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">
  <style>
    .title {{ font: 700 34px system-ui, -apple-system, Segoe UI, sans-serif; fill: #111827; }}
    .verdict {{ font: 800 42px system-ui, -apple-system, Segoe UI, sans-serif; fill: {accent}; }}
    .body {{ font: 24px system-ui, -apple-system, Segoe UI, sans-serif; fill: #1F2937; }}
    .foot {{ font: 20px system-ui, -apple-system, Segoe UI, sans-serif; fill: #6B7280; }}
  </style>
  <rect width="1200" height="{height}" rx="28" fill="#F9FAFB"/>
  <rect x="22" y="22" width="1156" height="{height - 44}" rx="24" fill="#FFFFFF" stroke="#D1D5DB" stroke-width="2"/>
  <text x="42" y="72" class="title">X Algorithm Claim Audit</text>
  <text x="42" y="122" class="verdict">{html.escape(verdict_label)}</text>
  {''.join(text_parts)}
  <text x="42" y="{height - 42}" class="foot">Source: xai-org/x-algorithm @ {html.escape(str(commit))} | Public repo evidence only</text>
</svg>
"""


def build_audit(claim: str, repo: Path) -> dict[str, object]:
    rules, evidence = collect_evidence(repo, claim)
    classification = classify(claim, rules, evidence)
    repo_info = repo_metadata(repo)
    audit: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim": claim,
        "repo": repo_info,
        "triggered_rules": [rule.name for rule in rules],
        "evidence": [asdict(item) for item in evidence],
        **classification,
    }
    audit["share_prompt"] = (
        f"I audited this X algorithm claim against the public xai-org/x-algorithm repo. "
        f"Verdict: {audit['verdict']}. Evidence is tied to file paths and line numbers."
    )
    return audit


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claim_arg", nargs="?", help="Claim text to audit.")
    parser.add_argument("--claim", help="Claim text to audit.")
    parser.add_argument("--claim-file", help="File containing the claim text.")
    parser.add_argument("--repo-dir", help="Existing xai-org/x-algorithm checkout.")
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, help="Clone cache directory.")
    parser.add_argument("--output-dir", default="x-algo-claim-audit", help="Output directory.")
    parser.add_argument("--ref", default="main", help="Git ref to fetch when cloning.")
    parser.add_argument("--force-clone", action="store_true", help="Delete and recreate managed clone.")
    return parser.parse_args(argv)


def load_claim(args: argparse.Namespace) -> str:
    parts = []
    if args.claim:
        parts.append(args.claim)
    if args.claim_arg:
        parts.append(args.claim_arg)
    if args.claim_file:
        parts.append(read_text(Path(args.claim_file).expanduser()))
    claim = "\n".join(part.strip() for part in parts if part and part.strip()).strip()
    if not claim:
        raise SystemExit("Provide a claim via --claim, --claim-file, or positional text.")
    return claim


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    claim = load_claim(args)
    repo = ensure_repo(args)
    out = Path(args.output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    audit = build_audit(claim, repo)
    (out / "claim_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    (out / "claim_audit.md").write_text(render_markdown(audit) + "\n", encoding="utf-8")
    (out / "share_card.md").write_text(render_share_card_md(audit) + "\n", encoding="utf-8")
    (out / "share_card.svg").write_text(render_share_card_svg(audit), encoding="utf-8")

    print(f"Wrote {out / 'claim_audit.md'}")
    print(f"Wrote {out / 'claim_audit.json'}")
    print(f"Wrote {out / 'share_card.md'}")
    print(f"Wrote {out / 'share_card.svg'}")
    print(f"Verdict: {audit['verdict']} ({audit['confidence']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
