#!/usr/bin/env python3
"""Local public bundle checks for Open Feed Recsys Lab skills."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "open-feed-recsys-lab": {
        "path": ROOT / "skill" / "open-feed-recsys-lab",
        "script": ROOT / "skill" / "open-feed-recsys-lab" / "scripts" / "open_feed_recsys_lab.py",
        "required": ["SKILL.md", "agents/openai.yaml", "references/product-gate.md", "scripts/open_feed_recsys_lab.py"],
    },
    "x-algo-claim-auditor": {
        "path": ROOT / "skill" / "x-algo-claim-auditor",
        "script": ROOT / "skill" / "x-algo-claim-auditor" / "scripts" / "x_algo_claim_auditor.py",
        "required": ["SKILL.md", "agents/openai.yaml", "references/claim-boundaries.md", "scripts/x_algo_claim_auditor.py"],
    },
    "tinytroupe-feed-research-lab": {
        "path": ROOT / "skill" / "tinytroupe-feed-research-lab",
        "script": ROOT / "skill" / "tinytroupe-feed-research-lab" / "scripts" / "tinytroupe_feed_research_lab.py",
        "required": [
            "SKILL.md",
            "agents/openai.yaml",
            "references/research-boundaries.md",
            "scripts/tinytroupe_feed_research_lab.py",
        ],
    },
}


REQUIRED = [
    ROOT / "README.md",
    ROOT / "LICENSE",
]

BLOCKED_PATTERNS = [
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def check_required() -> None:
    paths = list(REQUIRED)
    for spec in SKILLS.values():
        skill_path = spec["path"]
        paths.extend(skill_path / rel for rel in spec["required"])
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_no_cache_files() -> None:
    listed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if listed.returncode != 0:
        return
    paths = [ROOT / line for line in listed.stdout.splitlines() if line]
    bad = [path for path in paths if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}]
    if bad:
        fail(f"cache files should not be published: {[str(p.relative_to(ROOT)) for p in bad]}")


def check_frontmatter() -> None:
    for name, spec in SKILLS.items():
        skill_md = spec["path"] / "SKILL.md"
        text = read(skill_md)
        if not text.startswith("---\n"):
            fail(f"{skill_md.relative_to(ROOT)} is missing YAML frontmatter")
        end = text.find("\n---", 4)
        if end == -1:
            fail(f"{skill_md.relative_to(ROOT)} frontmatter is not closed")
        frontmatter = text[4:end]
        for field in ["name:", "description:"]:
            if field not in frontmatter:
                fail(f"{skill_md.relative_to(ROOT)} frontmatter missing {field}")


def check_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {"", ".md", ".py", ".toml", ".yaml", ".yml", ".json", ".txt"}:
            continue
        text = read(path)
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(text):
                fail(f"blocked secret-like pattern in {path.relative_to(ROOT)}")


def check_compile() -> None:
    scripts = [spec["script"] for spec in SKILLS.values()]
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, scripts)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        fail(proc.stderr.strip())


def main() -> int:
    check_required()
    check_no_cache_files()
    check_frontmatter()
    check_secrets()
    check_compile()
    print("skill bundle check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
