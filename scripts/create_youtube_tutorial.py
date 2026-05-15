#!/usr/bin/env python3
"""Create a YouTube tutorial video for Open Feed Recsys Lab.

Requires macOS `say`, ffmpeg, and Pillow. The output video is generated under
out/youtube/ and is intentionally not committed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "youtube"
W, H = 1920, 1080
BG = (247, 249, 248)
INK = (21, 32, 38)
MUTED = (82, 101, 110)
ACCENT = (23, 107, 91)
PANEL = (255, 255, 255)
LINE = (215, 224, 228)
CODE_BG = (15, 23, 26)
CODE_INK = (233, 245, 242)


SLIDES = [
    {
        "title": "Verify the open X For You algorithm repo locally",
        "body": [
            "Open Feed Recsys Lab turns xai-org/x-algorithm into a commit-pinned report.",
            "It checks source, Phoenix artifacts, documentation drift, and architecture maps before anyone overclaims what was reproduced.",
        ],
        "code": "github.com/zack-dev-cm/open-feed-recsys-lab",
        "voice": "Open Feed Recsys Lab verifies the open X For You algorithm repository locally. It creates a commit pinned report, checks Phoenix artifacts, detects documentation drift, and generates an architecture map before anyone overclaims what was reproduced.",
    },
    {
        "title": "Why a clone is not a full model run",
        "body": [
            "The repo source is inspectable immediately.",
            "Phoenix inference needs the official extracted Git LFS artifact first.",
            "The lab separates source inspection from runnable inference.",
        ],
        "code": "Phoenix run ready: false until artifacts/oss-phoenix-artifacts exists",
        "voice": "A lightweight clone is useful, but it is not the same thing as a full Phoenix model run. Phoenix inference needs the official extracted Git LFS artifact. The lab makes that boundary explicit.",
    },
    {
        "title": "One command creates four artifacts",
        "body": [
            "run_report.md records commit, repo status, components, and warnings.",
            "artifact_check.md records LFS and Phoenix readiness.",
            "architecture_map.html is the shareable visual artifact.",
            "manifest.json is the machine-readable source of truth.",
        ],
        "code": "python3 skill/open-feed-recsys-lab/scripts/open_feed_recsys_lab.py",
        "voice": "One command creates four artifacts. The run report records the commit and component inventory. The artifact check records Git LFS and Phoenix readiness. The architecture map is the shareable visual output. The manifest is machine readable.",
    },
    {
        "title": "The current repo has useful reproducibility signals",
        "body": [
            "A lightweight clone shows the Phoenix zip as a 3.12 GB Git LFS pointer.",
            "The public docs currently disagree on mini-model embedding size and layer count.",
            "That is exactly what a reproducibility report should surface.",
        ],
        "code": "README emb_size=256, layers=2 | phoenix/README emb_size=128, layers=4",
        "voice": "On the current public repo, a lightweight clone shows the Phoenix zip as a three point one two gigabyte Git LFS pointer. The docs also disagree on mini model embedding size and layer count. These are exactly the signals a reproducibility report should surface.",
    },
    {
        "title": "Use it with Codex, Claude Code, or ClawHub",
        "body": [
            "Install from ClawHub as open-feed-recsys-lab.",
            "Use the GitHub repo as the canonical source.",
            "Do not use it as a growth hack or reach predictor.",
        ],
        "code": "clawhub install open-feed-recsys-lab",
        "voice": "Use Open Feed Recsys Lab with Codex, Claude Code, or ClawHub when you need a concrete local artifact. Install it from ClawHub, or use the GitHub repo directly. This is not a growth hack and it does not predict reach.",
    },
]


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr}")


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Supplemental/Verdana.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False)


def draw_slide(path: Path, index: int, slide: dict[str, object]) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_font = font(74, bold=True)
    body_font = font(38)
    code_font = font(34, mono=True)
    small_font = font(28, bold=True)

    d.rectangle((0, 0, W, 112), fill=PANEL)
    d.text((84, 38), "Open Feed Recsys Lab", fill=ACCENT, font=small_font)
    d.text((W - 250, 38), f"{index + 1}/{len(SLIDES)}", fill=MUTED, font=small_font)

    y = 170
    for line in wrap(str(slide["title"]), 34):
        d.text((84, y), line, fill=INK, font=title_font)
        y += 86

    y += 28
    for item in slide["body"]:  # type: ignore[index]
        d.ellipse((92, y + 16, 108, y + 32), fill=ACCENT)
        for j, line in enumerate(wrap(str(item), 64)):
            d.text((130, y + j * 48), line, fill=INK, font=body_font)
        y += 105

    code = str(slide["code"])
    box_y = H - 220
    d.rounded_rectangle((84, box_y, W - 84, H - 92), radius=18, fill=CODE_BG)
    for i, line in enumerate(wrap(code, 68)):
        d.text((122, box_y + 38 + i * 44), line, fill=CODE_INK, font=code_font)

    img.save(path)


def draw_thumbnail(path: Path) -> None:
    img = Image.new("RGB", (1280, 720), BG)
    d = ImageDraw.Draw(img)
    title_font = font(72, bold=True)
    label_font = font(32, bold=True)
    d.rounded_rectangle((54, 52, 1226, 668), radius=28, fill=PANEL, outline=LINE, width=3)
    d.text((92, 88), "OPEN FEED RECSYS LAB", fill=ACCENT, font=label_font)
    y = 170
    for line in ["Verify the X For You", "algorithm repo locally"]:
        d.text((92, y), line, fill=INK, font=title_font)
        y += 84
    d.rounded_rectangle((92, 470, 1188, 586), radius=16, fill=CODE_BG)
    d.text((128, 510), "Phoenix artifacts + doc drift + architecture map", fill=CODE_INK, font=font(30, mono=True))
    img.save(path, quality=92)


def create(args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    segment_paths = []
    for i, slide in enumerate(SLIDES):
        image_path = OUT / f"slide_{i + 1:02d}.png"
        audio_path = OUT / f"slide_{i + 1:02d}.aiff"
        segment_path = OUT / f"segment_{i + 1:02d}.mp4"
        draw_slide(image_path, i, slide)
        run(["say", "-v", args.voice, "-r", str(args.rate), "-o", str(audio_path), str(slide["voice"])])
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(image_path),
                "-i",
                str(audio_path),
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                str(segment_path),
            ]
        )
        segment_paths.append(segment_path)

    concat_file = OUT / "concat.txt"
    concat_file.write_text("\n".join(f"file '{path}'" for path in segment_paths), encoding="utf-8")
    final = OUT / "open-feed-recsys-lab-youtube-tutorial.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(final)])
    draw_thumbnail(OUT / "open-feed-recsys-lab-thumbnail.jpg")
    (OUT / "narration.txt").write_text("\n\n".join(str(slide["voice"]) for slide in SLIDES), encoding="utf-8")
    print(final)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default="Samantha")
    parser.add_argument("--rate", type=int, default=178)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        create(parse_args(argv))
    except Exception as exc:
        print(f"create_youtube_tutorial failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
