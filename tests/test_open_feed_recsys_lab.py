from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "open-feed-recsys-lab" / "scripts" / "open_feed_recsys_lab.py"


class OpenFeedRecsysLabTest(unittest.TestCase):
    def make_fixture_repo(self, root: Path) -> Path:
        repo = root / "x-algorithm"
        for rel in [
            "home-mixer/candidate_pipeline",
            "home-mixer/scorers",
            "home-mixer/ads",
            "phoenix/artifacts",
            "grox/classifiers/content",
            "grox/tasks",
            "thunder/posts",
            "thunder/kafka",
            "candidate-pipeline",
        ]:
            (repo / rel).mkdir(parents=True, exist_ok=True)

        (repo / "README.md").write_text(
            "# X For You Feed Algorithm\n\nmini Phoenix model (256-dim embeddings, 4 attention heads, 2 transformer layers)\n",
            encoding="utf-8",
        )
        (repo / "phoenix" / "README.md").write_text(
            "\n".join(
                [
                    "# Phoenix",
                    "| Parameter | Value |",
                    "|---|---|",
                    "| Embedding dimension | 128 |",
                    "| Attention heads | 4 |",
                    "| Transformer layers | 4 |",
                    "| History sequence length | 127 |",
                    "| Candidate sequence length | 64 |",
                ]
            ),
            encoding="utf-8",
        )
        (repo / "phoenix" / "artifacts" / "oss-phoenix-artifacts.zip").write_text(
            "\n".join(
                [
                    "version https://git-lfs.github.com/spec/v1",
                    "oid sha256:abc123",
                    "size 3123149995",
                ]
            ),
            encoding="utf-8",
        )

        for rel in [
            "home-mixer/candidate_pipeline/for_you_candidate_pipeline.rs",
            "home-mixer/server.rs",
            "home-mixer/scorers/ranking_scorer.rs",
            "home-mixer/ads/safe_gap_blender.rs",
            "phoenix/run_pipeline.py",
            "phoenix/recsys_model.py",
            "phoenix/recsys_retrieval_model.py",
            "grox/engine.py",
            "grox/dispatcher.py",
            "thunder/thunder_service.rs",
            "thunder/posts/post_store.rs",
            "thunder/kafka/tweet_events_listener.rs",
            "candidate-pipeline/candidate_pipeline.rs",
            "candidate-pipeline/source.rs",
            "candidate-pipeline/hydrator.rs",
            "candidate-pipeline/filter.rs",
            "candidate-pipeline/scorer.rs",
            "candidate-pipeline/selector.rs",
            "candidate-pipeline/side_effect.rs",
        ]:
            (repo / rel).write_text("// fixture\n", encoding="utf-8")

        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "fixture", "-q"],
            cwd=repo,
            check=True,
        )
        return repo

    def test_report_generation_detects_artifacts_and_doc_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_fixture_repo(root)
            out = root / "report"

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-dir",
                    str(repo),
                    "--output-dir",
                    str(out),
                    "--no-github-api",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["artifacts"]["ready_for_phoenix_run"])
            self.assertTrue(manifest["artifacts"]["zip_lfs_pointer"])
            self.assertIn(
                "README.md and phoenix/README.md disagree on emb_size: [256] vs [128]",
                manifest["docs"]["mismatches_or_unknowns"],
            )
            self.assertTrue((out / "architecture_map.html").exists())

    def test_bundle_check_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_skill_bundle.py")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
