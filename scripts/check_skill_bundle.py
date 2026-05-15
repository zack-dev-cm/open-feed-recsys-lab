#!/usr/bin/env python3
"""Local public bundle checks for Open Feed Recsys Lab."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "open-feed-recsys-lab"
SCRIPT = SKILL / "scripts" / "open_feed_recsys_lab.py"


REQUIRED = [
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "product-gate.md",
    SCRIPT,
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
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
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
    text = read(SKILL / "SKILL.md")
    if not text.startswith("---\n"):
        fail("SKILL.md is missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        fail("SKILL.md frontmatter is not closed")
    frontmatter = text[4:end]
    for field in ["name:", "description:", "license:", "metadata:"]:
        if field not in frontmatter:
            fail(f"SKILL.md frontmatter missing {field}")
    if '"skillKey":"open-feed-recsys-lab"' not in frontmatter:
        fail("metadata.openclaw.skillKey must be open-feed-recsys-lab")


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
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCRIPT)],
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
