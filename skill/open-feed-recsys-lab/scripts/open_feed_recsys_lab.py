#!/usr/bin/env python3
"""Generate a reproducibility and architecture report for open feed recsys repos.

The default target is https://github.com/xai-org/x-algorithm. The script avoids
downloading Git LFS payloads unless the caller explicitly prepares them; it is
intended to make a repo understandable and locally verifiable before heavy runs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_REPO = "https://github.com/xai-org/x-algorithm"
DEFAULT_REF = "main"
DEFAULT_USER_AGENT = "open-feed-recsys-lab/0.1"

COMPONENTS = {
    "home-mixer": {
        "role": "Feed orchestration layer",
        "evidence": [
            "candidate_pipeline/for_you_candidate_pipeline.rs",
            "server.rs",
            "scorers/ranking_scorer.rs",
            "ads/safe_gap_blender.rs",
        ],
        "checks": [
            "Sources, query hydrators, filters, scorers, selector, side effects",
            "Ads blending and brand-safety boundary logic",
        ],
    },
    "phoenix": {
        "role": "JAX/Haiku retrieval and ranking demo",
        "evidence": [
            "run_pipeline.py",
            "recsys_model.py",
            "recsys_retrieval_model.py",
            "README.md",
        ],
        "checks": [
            "Runnable path depends on extracted LFS artifacts",
            "Docs/config consistency for mini model dimensions and layers",
        ],
    },
    "grox": {
        "role": "Content understanding task engine",
        "evidence": [
            "engine.py",
            "dispatcher.py",
            "classifiers/content",
            "tasks",
        ],
        "checks": [
            "Classifier/task inventory",
            "Non-runnable imports or internal service dependencies",
        ],
    },
    "thunder": {
        "role": "In-network recent post store and Kafka ingestion service",
        "evidence": [
            "thunder_service.rs",
            "posts/post_store.rs",
            "kafka/tweet_events_listener.rs",
        ],
        "checks": [
            "In-memory store behavior",
            "Kafka and production dependency boundaries",
        ],
    },
    "candidate-pipeline": {
        "role": "Reusable Rust pipeline framework",
        "evidence": [
            "candidate_pipeline.rs",
            "source.rs",
            "hydrator.rs",
            "filter.rs",
            "scorer.rs",
            "selector.rs",
            "side_effect.rs",
        ],
        "checks": [
            "Pipeline stages and parallel execution",
            "Scaffoldable abstractions for other apps",
        ],
    },
}


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def safe_run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    try:
        return run(cmd, cwd=cwd, env=env)
    except Exception as exc:
        return f"ERROR: {exc}"


def run_status(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def checkout_ref(repo_dir: Path, ref: str) -> None:
    if not ref:
        return
    current_branch = safe_run(["git", "branch", "--show-current"], cwd=repo_dir)
    if ref == current_branch:
        return
    current_head = safe_run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
    if current_head.startswith(ref):
        return

    checkout = run_status(["git", "checkout", "--detach", ref], cwd=repo_dir)
    if checkout.returncode == 0:
        return

    fetch = run_status(["git", "fetch", "--depth", "1", "origin", ref], cwd=repo_dir)
    if fetch.returncode == 0:
        run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=repo_dir)
        return

    raise RuntimeError(
        "Could not checkout requested ref "
        f"{ref!r}.\ncheckout stderr: {checkout.stderr.strip()}\nfetch stderr: {fetch.stderr.strip()}"
    )


def ensure_repo(repo_url: str, ref: str, repo_dir: Path, force: bool) -> Path:
    if repo_dir.exists() and force:
        shutil.rmtree(repo_dir)

    if not repo_dir.exists():
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        run(["git", "clone", "--depth", "1", repo_url, str(repo_dir)], env=env)
        checkout_ref(repo_dir, ref)
    elif not (repo_dir / ".git").exists():
        raise RuntimeError(f"{repo_dir} exists but is not a git repository")

    return repo_dir


def read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    data = path.read_text(encoding="utf-8", errors="replace")
    return data if limit is None else data[:limit]


def github_api(repo_url: str) -> dict[str, Any] | None:
    m = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", repo_url)
    if not m:
        return None
    url = f"https://api.github.com/repos/{m.group('owner')}/{m.group('repo')}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def git_facts(repo_dir: Path) -> dict[str, str]:
    return {
        "head": safe_run(["git", "rev-parse", "HEAD"], cwd=repo_dir),
        "head_short": safe_run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir),
        "branch": safe_run(["git", "branch", "--show-current"], cwd=repo_dir),
        "last_commit": safe_run(["git", "log", "-1", "--pretty=%h %cI %s"], cwd=repo_dir),
        "status": safe_run(["git", "status", "--short"], cwd=repo_dir) or "clean",
    }


def ref_warning(requested_ref: str, repo_dir: Path) -> str | None:
    if not requested_ref:
        return None
    branch = safe_run(["git", "branch", "--show-current"], cwd=repo_dir)
    head = safe_run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
    if requested_ref == branch or head.startswith(requested_ref):
        return None
    if requested_ref == "main" and branch == "main":
        return None
    return (
        f"Requested ref `{requested_ref}` is not obviously satisfied by current branch `{branch}` "
        f"or HEAD `{head}`. Existing repo checkouts are not mutated unless cloned by this script."
    )


def file_inventory(repo_dir: Path) -> dict[str, Any]:
    files = [p for p in repo_dir.rglob("*") if p.is_file() and ".git" not in p.parts]
    suffix_bytes: dict[str, int] = {}
    top_dirs: dict[str, int] = {}
    top_files: list[str] = []
    for path in files:
        rel = path.relative_to(repo_dir)
        suffix = path.suffix.lower() or "[no suffix]"
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        suffix_bytes[suffix] = suffix_bytes.get(suffix, 0) + size
        if len(rel.parts) == 1:
            top_files.append(rel.parts[0])
        else:
            top = rel.parts[0]
            top_dirs[top] = top_dirs.get(top, 0) + 1
    return {
        "file_count": len(files),
        "suffix_bytes": dict(sorted(suffix_bytes.items(), key=lambda x: x[1], reverse=True)[:12]),
        "top_dirs": dict(sorted(top_dirs.items(), key=lambda x: x[1], reverse=True)),
        "top_files": sorted(top_files),
    }


def parse_lfs_pointer(path: Path) -> dict[str, str] | None:
    text = read_text(path, limit=300)
    if not text.startswith("version https://git-lfs.github.com/spec/v1"):
        return None
    facts: dict[str, str] = {"path": str(path)}
    for line in text.splitlines():
        if line.startswith("oid "):
            facts["oid"] = line.split(" ", 1)[1]
        elif line.startswith("size "):
            facts["size"] = line.split(" ", 1)[1]
    return facts


def artifact_checks(repo_dir: Path, artifacts_dir: Path | None) -> dict[str, Any]:
    zip_path = repo_dir / "phoenix" / "artifacts" / "oss-phoenix-artifacts.zip"
    pointer = parse_lfs_pointer(zip_path)
    extracted = artifacts_dir or repo_dir / "phoenix" / "artifacts" / "oss-phoenix-artifacts"
    expected = [
        extracted / "retrieval" / "model_params.npz",
        extracted / "retrieval" / "embedding_tables.npz",
        extracted / "retrieval" / "config.json",
        extracted / "ranker" / "model_params.npz",
        extracted / "ranker" / "embedding_tables.npz",
        extracted / "ranker" / "config.json",
        extracted / "sports_corpus.npz",
        extracted / "example_sequence.json",
    ]
    existing = [p for p in expected if p.exists()]
    configs: dict[str, Any] = {}
    for name, cfg_path in {
        "retrieval_config": extracted / "retrieval" / "config.json",
        "ranker_config": extracted / "ranker" / "config.json",
    }.items():
        if cfg_path.exists():
            try:
                configs[name] = json.loads(cfg_path.read_text(encoding="utf-8"))
            except Exception as exc:
                configs[name] = {"error": str(exc)}
    return {
        "zip_path": str(zip_path.relative_to(repo_dir)) if zip_path.exists() else "missing",
        "zip_lfs_pointer": pointer,
        "extracted_dir": str(extracted),
        "expected_files": [str(p) for p in expected],
        "existing_files": [str(p) for p in existing],
        "ready_for_phoenix_run": len(existing) == len(expected),
        "configs": configs,
    }


def extract_model_claims(text: str) -> list[str]:
    claims: list[str] = []
    patterns = [
        r"(\d+)-dim(?:ensional)? embeddings?",
        r"Embedding dimension\s*\|\s*(\d+)",
        r"(\d+) attention heads?",
        r"Attention heads\s*\|\s*(\d+)",
        r"(\d+) transformer layers?",
        r"Transformer layers\s*\|\s*(\d+)",
        r"History sequence length\s*\|\s*(\d+)",
        r"Candidate sequence length\s*\|\s*(\d+)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            claims.append(m.group(0).strip())
    return sorted(set(claims))


def add_metric(metrics: dict[str, set[int]], key: str, value: str) -> None:
    metrics.setdefault(key, set()).add(int(value))


def extract_model_metrics(text: str) -> dict[str, list[int]]:
    metrics: dict[str, set[int]] = {}
    patterns = [
        (r"(\d+)-dim(?:ensional)? embeddings?", "emb_size"),
        (r"Embedding dimension\s*\|\s*(\d+)", "emb_size"),
        (r"(\d+) attention heads?", "num_heads"),
        (r"Attention heads\s*\|\s*(\d+)", "num_heads"),
        (r"(\d+) transformer layers?", "num_layers"),
        (r"Transformer layers\s*\|\s*(\d+)", "num_layers"),
        (r"History sequence length\s*\|\s*(\d+)", "history_seq_len"),
        (r"Candidate sequence length\s*\|\s*(\d+)", "candidate_seq_len"),
    ]
    for pattern, key in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            add_metric(metrics, key, match.group(1))
    return {key: sorted(values) for key, values in sorted(metrics.items())}


def doc_checks(repo_dir: Path, artifacts: dict[str, Any]) -> dict[str, Any]:
    root_readme = read_text(repo_dir / "README.md")
    phoenix_readme = read_text(repo_dir / "phoenix" / "README.md")
    root_claims = extract_model_claims(root_readme)
    phoenix_claims = extract_model_claims(phoenix_readme)
    root_metrics = extract_model_metrics(root_readme)
    phoenix_metrics = extract_model_metrics(phoenix_readme)

    config_claims: list[str] = []
    config_metrics: dict[str, set[int]] = {}
    for cfg in artifacts.get("configs", {}).values():
        if isinstance(cfg, dict) and "error" not in cfg:
            for key in ["emb_size", "num_heads", "num_layers", "history_seq_len", "candidate_seq_len"]:
                if key in cfg:
                    config_claims.append(f"{key}={cfg[key]}")
                    config_metrics.setdefault(key, set()).add(int(cfg[key]))

    mismatches: list[str] = []
    for key in sorted(set(root_metrics) & set(phoenix_metrics)):
        if root_metrics[key] != phoenix_metrics[key]:
            mismatches.append(
                f"README.md and phoenix/README.md disagree on {key}: "
                f"{root_metrics[key]} vs {phoenix_metrics[key]}"
            )
    if config_claims:
        for key, values in sorted(config_metrics.items()):
            config_values = sorted(values)
            for label, metrics in [("README.md", root_metrics), ("phoenix/README.md", phoenix_metrics)]:
                if key in metrics and metrics[key] != config_values:
                    mismatches.append(
                        f"{label} and extracted configs disagree on {key}: "
                        f"{metrics[key]} vs {config_values}"
                    )
    else:
        mismatches.append("No extracted Phoenix config JSON found; cannot validate docs against artifacts")

    return {
        "root_readme_claims": root_claims,
        "phoenix_readme_claims": phoenix_claims,
        "root_readme_metrics": root_metrics,
        "phoenix_readme_metrics": phoenix_metrics,
        "config_claims": sorted(set(config_claims)),
        "config_metrics": {key: sorted(values) for key, values in sorted(config_metrics.items())},
        "mismatches_or_unknowns": mismatches,
    }


def component_checks(repo_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component, meta in COMPONENTS.items():
        comp_dir = repo_dir / component
        evidence = []
        for rel in meta["evidence"]:
            exists = (comp_dir / rel).exists()
            evidence.append({"path": f"{component}/{rel}", "exists": exists})
        rows.append(
            {
                "component": component,
                "role": meta["role"],
                "present": comp_dir.exists(),
                "evidence": evidence,
                "checks": meta["checks"],
            }
        )
    return rows


def optional_command_checks(repo_dir: Path, run_pytest: bool, run_phoenix: bool, artifacts: dict[str, Any]) -> dict[str, str]:
    checks: dict[str, str] = {}
    if run_pytest:
        checks["phoenix_pytest"] = safe_run(
            ["uv", "run", "pytest", "test_recsys_model.py", "test_recsys_retrieval_model.py"],
            cwd=repo_dir / "phoenix",
        )
    if run_phoenix:
        if artifacts.get("ready_for_phoenix_run"):
            checks["phoenix_run_pipeline"] = safe_run(
                ["uv", "run", "run_pipeline.py", "--artifacts_dir", artifacts["extracted_dir"]],
                cwd=repo_dir / "phoenix",
            )
        else:
            checks["phoenix_run_pipeline"] = "SKIPPED: extracted LFS artifacts are incomplete"
    return checks


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(cell.replace("\n", "<br>") for cell in row) + " |" for row in rows)
    return "\n".join(out)


def render_artifact_check(data: dict[str, Any]) -> str:
    pointer = data["artifacts"].get("zip_lfs_pointer")
    pointer_text = "not an LFS pointer"
    if pointer:
        size = int(pointer.get("size", "0"))
        pointer_text = f"{size:,} bytes ({size / 1_000_000_000:.2f} GB), {pointer.get('oid', '')}"
    existing = len(data["artifacts"]["existing_files"])
    expected = len(data["artifacts"]["expected_files"])
    lines = [
        "# Artifact Check",
        "",
        f"- Repository: `{data['repo_url']}`",
        f"- Requested ref: `{data['requested_ref']}`",
        f"- Commit: `{data['git']['head']}`",
        f"- LFS archive: `{data['artifacts']['zip_path']}`",
        f"- LFS pointer: {pointer_text}",
        f"- Extracted artifacts dir: `{data['artifacts']['extracted_dir']}`",
        f"- Phoenix run ready: `{data['artifacts']['ready_for_phoenix_run']}` ({existing}/{expected} files present)",
        "",
        "## Missing Files",
        "",
    ]
    missing = sorted(set(data["artifacts"]["expected_files"]) - set(data["artifacts"]["existing_files"]))
    if missing:
        lines.extend(f"- `{m}`" for m in missing)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Doc/Config Checks",
            "",
            f"- Root README claims: `{', '.join(data['docs']['root_readme_claims']) or 'none found'}`",
            f"- Phoenix README claims: `{', '.join(data['docs']['phoenix_readme_claims']) or 'none found'}`",
            f"- Extracted config claims: `{', '.join(data['docs']['config_claims']) or 'none found'}`",
            "",
        ]
    )
    unknowns = data["docs"]["mismatches_or_unknowns"]
    if unknowns:
        lines.append("## Mismatches Or Unknowns")
        lines.append("")
        lines.extend(f"- {item}" for item in unknowns)
    return "\n".join(lines) + "\n"


def render_run_report(data: dict[str, Any]) -> str:
    meta = data.get("github") or {}
    rows = []
    for comp in data["components"]:
        present = "yes" if comp["present"] else "no"
        evidence = ", ".join(
            f"`{e['path']}`" + ("" if e["exists"] else " (missing)") for e in comp["evidence"]
        )
        rows.append([comp["component"], present, comp["role"], evidence])

    lines = [
        "# Open Feed Recsys Lab Report",
        "",
        f"- Generated: {data['generated_at']}",
        f"- Repository: `{data['repo_url']}`",
        f"- Requested ref: `{data['requested_ref']}`",
        f"- Commit: `{data['git']['head']}`",
        f"- Last commit: `{data['git']['last_commit']}`",
        f"- Git status: `{data['git']['status']}`",
    ]
    if meta:
        lines.extend(
            [
                f"- GitHub stars: {meta.get('stargazers_count', 'unknown')}",
                f"- GitHub forks: {meta.get('forks_count', 'unknown')}",
                f"- GitHub pushed_at: {meta.get('pushed_at', 'unknown')}",
                f"- License: {(meta.get('license') or {}).get('spdx_id', 'unknown')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            readiness_verdict(data),
            "",
            "## Warnings",
            "",
        ]
    )
    if data["warnings"]:
        lines.extend(f"- {warning}" for warning in data["warnings"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Components",
            "",
            markdown_table(["Component", "Present", "Role", "Evidence"], rows),
            "",
            "## Artifact Readiness",
            "",
            f"- LFS archive pointer found: `{bool(data['artifacts'].get('zip_lfs_pointer'))}`",
            f"- Extracted artifacts complete: `{data['artifacts']['ready_for_phoenix_run']}`",
            f"- Expected artifact files present: {len(data['artifacts']['existing_files'])}/{len(data['artifacts']['expected_files'])}",
            "",
            "## Documentation Checks",
            "",
        ]
    )
    unknowns = data["docs"]["mismatches_or_unknowns"]
    if unknowns:
        lines.extend(f"- {item}" for item in unknowns)
    else:
        lines.append("- No obvious doc/config mismatch found.")
    lines.extend(
        [
            "",
            "## Inventory",
            "",
            f"- File count: {data['inventory']['file_count']}",
            f"- Top directories: `{json.dumps(data['inventory']['top_dirs'], sort_keys=True)}`",
            f"- Top-level files: `{json.dumps(data['inventory']['top_files'])}`",
            f"- Largest suffix groups: `{json.dumps(data['inventory']['suffix_bytes'], sort_keys=True)}`",
            "",
            "## Optional Command Checks",
            "",
        ]
    )
    if data["commands"]:
        for name, output in data["commands"].items():
            lines.extend([f"### {name}", "", "```text", output[:6000], "```", ""])
    else:
        lines.append("- Not requested. Use `--run-pytest` or `--run-phoenix` after dependencies/artifacts are ready.")
    return "\n".join(lines) + "\n"


def readiness_verdict(data: dict[str, Any]) -> str:
    if data["artifacts"]["ready_for_phoenix_run"]:
        return "Phoenix artifacts are present. The repo is ready for a local Phoenix run check."
    return (
        "Source inspection is ready, but Phoenix execution is blocked until the Git LFS archive is "
        "downloaded and extracted. This is expected for a lightweight clone."
    )


def render_architecture_map(data: dict[str, Any]) -> str:
    cards = []
    for comp in data["components"]:
        evidence = "".join(
            f"<li><code>{html.escape(e['path'])}</code>{'' if e['exists'] else ' <strong>missing</strong>'}</li>"
            for e in comp["evidence"]
        )
        checks = "".join(f"<li>{html.escape(c)}</li>" for c in comp["checks"])
        cards.append(
            f"""
            <section class="card">
              <h2>{html.escape(comp['component'])}</h2>
              <p>{html.escape(comp['role'])}</p>
              <h3>Evidence</h3>
              <ul>{evidence}</ul>
              <h3>Review Checks</h3>
              <ul>{checks}</ul>
            </section>
            """
        )

    graph = """
    <div class="flow">
      <div class="node request">Feed Request</div>
      <div class="arrow">-></div>
      <div class="node">Home Mixer</div>
      <div class="arrow">-></div>
      <div class="split">
        <div class="node">Thunder<br><span>in-network</span></div>
        <div class="node">Phoenix<br><span>out-of-network</span></div>
        <div class="node">Ads / Prompts / Who To Follow</div>
      </div>
      <div class="arrow">-></div>
      <div class="node">Hydrate / Filter / Score</div>
      <div class="arrow">-></div>
      <div class="node response">Ranked Feed</div>
    </div>
    """

    return textwrap.dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Open Feed Recsys Architecture Map</title>
          <style>
            :root {{
              color-scheme: light;
              --ink: #172126;
              --muted: #5d6b72;
              --line: #d7dee2;
              --panel: #ffffff;
              --bg: #f6f8f7;
              --accent: #24735f;
              --accent-2: #914f26;
            }}
            * {{ box-sizing: border-box; }}
            body {{
              margin: 0;
              font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              color: var(--ink);
              background: var(--bg);
              line-height: 1.45;
            }}
            header {{
              padding: 32px clamp(18px, 4vw, 56px) 20px;
              border-bottom: 1px solid var(--line);
              background: #ffffff;
            }}
            h1 {{ margin: 0 0 8px; font-size: clamp(26px, 4vw, 46px); letter-spacing: 0; }}
            header p {{ margin: 4px 0; color: var(--muted); }}
            main {{ padding: 24px clamp(18px, 4vw, 56px) 48px; }}
            .summary {{
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
              gap: 12px;
              margin-bottom: 22px;
            }}
            .metric {{
              background: var(--panel);
              border: 1px solid var(--line);
              border-radius: 8px;
              padding: 14px;
            }}
            .metric strong {{ display: block; font-size: 13px; color: var(--muted); margin-bottom: 4px; }}
            .flow {{
              display: flex;
              align-items: center;
              gap: 10px;
              overflow-x: auto;
              padding: 18px;
              background: #eef4f1;
              border: 1px solid var(--line);
              border-radius: 8px;
              margin-bottom: 22px;
            }}
            .node {{
              flex: 0 0 auto;
              min-width: 150px;
              padding: 14px 12px;
              border-radius: 8px;
              border: 1px solid #9eb7ad;
              background: #fff;
              text-align: center;
              font-weight: 650;
            }}
            .node span {{ font-size: 12px; color: var(--muted); font-weight: 500; }}
            .request {{ border-color: var(--accent); }}
            .response {{ border-color: var(--accent-2); }}
            .arrow {{ color: var(--muted); font-weight: 700; }}
            .split {{ display: flex; gap: 8px; }}
            .grid {{
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
              gap: 14px;
            }}
            .card {{
              background: var(--panel);
              border: 1px solid var(--line);
              border-radius: 8px;
              padding: 16px;
            }}
            .card h2 {{ margin: 0 0 6px; font-size: 20px; }}
            .card h3 {{ margin: 14px 0 6px; font-size: 13px; color: var(--muted); text-transform: uppercase; }}
            ul {{ padding-left: 18px; margin: 6px 0; }}
            code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.92em; }}
            @media (max-width: 760px) {{
              .flow {{ align-items: stretch; }}
              .split {{ flex-direction: column; }}
            }}
          </style>
        </head>
        <body>
          <header>
            <h1>Open Feed Recsys Architecture Map</h1>
            <p><strong>Repository:</strong> <code>{html.escape(data['repo_url'])}</code></p>
            <p><strong>Requested ref:</strong> <code>{html.escape(data['requested_ref'])}</code></p>
            <p><strong>Commit:</strong> <code>{html.escape(data['git']['head'])}</code></p>
            <p><strong>Generated:</strong> {html.escape(data['generated_at'])}</p>
          </header>
          <main>
            <section class="summary">
              <div class="metric"><strong>Phoenix Run Ready</strong>{data['artifacts']['ready_for_phoenix_run']}</div>
              <div class="metric"><strong>Files</strong>{data['inventory']['file_count']}</div>
              <div class="metric"><strong>Doc Checks</strong>{len(data['docs']['mismatches_or_unknowns'])} mismatch/unknown item(s)</div>
            </section>
            {graph}
            <section class="grid">
              {''.join(cards)}
            </section>
          </main>
        </body>
        </html>
        """
    )


def write_outputs(data: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_report.md").write_text(render_run_report(data), encoding="utf-8")
    (output_dir / "artifact_check.md").write_text(render_artifact_check(data), encoding="utf-8")
    (output_dir / "architecture_map.html").write_text(render_architecture_map(data), encoding="utf-8")
    (output_dir / "manifest.json").write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def build_data(args: argparse.Namespace) -> dict[str, Any]:
    repo_dir = ensure_repo(args.repo_url, args.ref, args.repo_dir, args.force_clone)
    artifacts = artifact_checks(repo_dir, args.artifacts_dir)
    warnings = [warning for warning in [ref_warning(args.ref, repo_dir)] if warning]
    data: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo_url": args.repo_url,
        "requested_ref": args.ref,
        "repo_dir": str(repo_dir),
        "git": git_facts(repo_dir),
        "github": github_api(args.repo_url) if not args.no_github_api else None,
        "inventory": file_inventory(repo_dir),
        "artifacts": artifacts,
        "docs": doc_checks(repo_dir, artifacts),
        "components": component_checks(repo_dir),
        "warnings": warnings,
        "commands": {},
    }
    data["commands"] = optional_command_checks(
        repo_dir,
        run_pytest=args.run_pytest,
        run_phoenix=args.run_phoenix,
        artifacts=artifacts,
    )
    return data


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-url", default=DEFAULT_REPO)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--repo-dir",
        type=Path,
        default=Path.cwd() / ".open-feed-recsys-lab" / "x-algorithm",
        help="Local clone path or existing repo path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "open-feed-recsys-lab-report",
        help="Directory for generated report artifacts.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=None,
        help="Extracted Phoenix artifacts directory. Defaults to repo/phoenix/artifacts/oss-phoenix-artifacts.",
    )
    parser.add_argument("--force-clone", action="store_true", help="Delete and recreate repo-dir.")
    parser.add_argument("--run-pytest", action="store_true", help="Run Phoenix pytest via uv.")
    parser.add_argument("--run-phoenix", action="store_true", help="Run Phoenix pipeline if artifacts are complete.")
    parser.add_argument("--no-github-api", action="store_true", help="Skip GitHub API metadata lookup.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        data = build_data(args)
        write_outputs(data, args.output_dir)
    except Exception as exc:
        print(f"open-feed-recsys-lab failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {args.output_dir / 'run_report.md'}")
    print(f"Wrote {args.output_dir / 'artifact_check.md'}")
    print(f"Wrote {args.output_dir / 'architecture_map.html'}")
    print(f"Wrote {args.output_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
