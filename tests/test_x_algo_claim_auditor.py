from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "x-algo-claim-auditor" / "scripts" / "x_algo_claim_auditor.py"


class XAlgoClaimAuditorTest(unittest.TestCase):
    def make_fixture_repo(self, root: Path) -> Path:
        repo = root / "x-algorithm"
        for rel in [
            "home-mixer/scorers",
            "home-mixer/filters",
            "home-mixer/ads",
            "home-mixer/sources",
            "home-mixer/candidate_hydrators",
            "home-mixer/selectors",
            "home-mixer/side_effects",
            "phoenix",
            "phoenix/artifacts",
            "grox/classifiers/content",
            "grox/tasks",
        ]:
            (repo / rel).mkdir(parents=True, exist_ok=True)

        (repo / "README.md").write_text(
            "\n".join(
                [
                    "# X For You Feed Algorithm",
                    "The Phoenix Grok-based transformer predicts probabilities for multiple engagement types.",
                    "The Weighted Scorer combines these into a final score.",
                    "Updates include a Grox content-understanding pipeline and ads blending system.",
                ]
            ),
            encoding="utf-8",
        )
        (repo / "home-mixer/scorers/ranking_scorer.rs").write_text(
            "\n".join(
                [
                    "let favorite = params.get(FavoriteWeight);",
                    "let reply = params.get(ReplyWeight);",
                    "let retweet = params.get(RetweetWeight);",
                    "let share = params.get(ShareWeight);",
                    "let dwell = params.get(DwellWeight);",
                    "let not_interested = params.get(NotInterestedWeight);",
                    "fn compute_weighted_score() {}",
                ]
            ),
            encoding="utf-8",
        )
        (repo / "home-mixer/scorers/weighted_scorer.rs").write_text(
            "Final Score = sum(weight_i * P(action_i))\n",
            encoding="utf-8",
        )
        (repo / "phoenix/README.md").write_text(
            "\n".join(
                [
                    "# Phoenix",
                    "Retrieval uses a two-tower model.",
                    "Ranking uses a Transformer with candidate isolation.",
                    "Candidates cannot attend to each other.",
                    "Download oss-phoenix-artifacts and sports_corpus before running.",
                ]
            ),
            encoding="utf-8",
        )
        (repo / "phoenix/run_pipeline.py").write_text("run_pipeline = True\n", encoding="utf-8")
        (repo / "phoenix/recsys_model.py").write_text("Transformer = object\n", encoding="utf-8")
        (repo / "phoenix/recsys_retrieval_model.py").write_text("Retrieval = object\n", encoding="utf-8")
        (repo / "phoenix/artifacts/oss-phoenix-artifacts.zip").write_text(
            "version https://git-lfs.github.com/spec/v1\n",
            encoding="utf-8",
        )
        (repo / "grox/engine.py").write_text("Grox content understanding engine\n", encoding="utf-8")
        (repo / "grox/dispatcher.py").write_text("dispatcher\n", encoding="utf-8")
        (repo / "grox/classifiers/content/reply_ranking.py").write_text(
            "class ReplyScorer: pass\nranked_replies_scores = True\n",
            encoding="utf-8",
        )
        (repo / "grox/classifiers/content/spam.py").write_text("spam classifier\n", encoding="utf-8")
        (repo / "grox/classifiers/content/safety_ptos.py").write_text("PTOS safety\n", encoding="utf-8")
        (repo / "grox/classifiers/content/banger_initial_screen.py").write_text(
            "class BangerInitialScreen: pass\n",
            encoding="utf-8",
        )
        (repo / "grox/tasks/task_spam_detection.py").write_text("spam task\n", encoding="utf-8")
        (repo / "grox/tasks/task_rank_replies.py").write_text("reply rank task\n", encoding="utf-8")
        (repo / "grox/tasks/task_post_safety_screen_deluxe.py").write_text(
            "post safety task\n",
            encoding="utf-8",
        )
        (repo / "home-mixer/ads/safe_gap_blender.rs").write_text("SafeGap BrandSafety ads blend\n", encoding="utf-8")
        (repo / "home-mixer/ads/partition_organic_blender.rs").write_text("ads blend\n", encoding="utf-8")
        (repo / "home-mixer/ads/util.rs").write_text("ads util\n", encoding="utf-8")
        (repo / "home-mixer/sources/ads_source.rs").write_text("struct AdsSource;\n", encoding="utf-8")
        (repo / "home-mixer/candidate_hydrators/ads_brand_safety_hydrator.rs").write_text(
            "BrandSafety hydrator\n",
            encoding="utf-8",
        )
        (repo / "home-mixer/candidate_hydrators/ads_brand_safety_vf_hydrator.rs").write_text(
            "BrandSafety vf hydrator\n",
            encoding="utf-8",
        )
        (repo / "home-mixer/selectors/blender_selector.rs").write_text("blend ads\n", encoding="utf-8")

        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "fixture", "-q"],
            cwd=repo,
            check=True,
        )
        return repo

    def run_audit(self, repo: Path, claim: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-dir",
                    str(repo),
                    "--claim",
                    claim,
                    "--output-dir",
                    str(out),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((out / "claim_audit.md").exists())
            self.assertTrue((out / "share_card.svg").exists())
            return json.loads((out / "claim_audit.json").read_text(encoding="utf-8"))

    def test_exact_reply_multiplier_is_misleading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_fixture_repo(Path(tmp))
            audit = self.run_audit(repo, "Replies are worth 150x a like in the new X algorithm")
            self.assertEqual(audit["verdict"], "misleading")
            self.assertTrue(any(item["file"].endswith("ranking_scorer.rs") for item in audit["evidence"]))

    def test_grox_claim_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_fixture_repo(Path(tmp))
            audit = self.run_audit(repo, "Grox includes spam detection and reply ranking")
            self.assertEqual(audit["verdict"], "supported")
            self.assertIn("grox_content_understanding", audit["triggered_rules"])

    def test_premium_boost_claim_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_fixture_repo(Path(tmp))
            audit = self.run_audit(repo, "Premium gets a visibility boost that widens every quarter")
            self.assertEqual(audit["verdict"], "unsupported")


if __name__ == "__main__":
    unittest.main()
