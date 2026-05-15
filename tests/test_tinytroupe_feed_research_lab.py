from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "tinytroupe-feed-research-lab" / "scripts" / "tinytroupe_feed_research_lab.py"


class TinyTroupeFeedResearchLabTest(unittest.TestCase):
    def run_lab(self, args: list[str]) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "feed-research"
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), *args, "--output-dir", str(out)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((out / "feed_research_report.md").exists())
            self.assertTrue((out / "persona_reactions.csv").exists())
            self.assertTrue((out / "share_card.svg").exists())
            self.assertTrue((out / "tinytroupe_experiment_plan.md").exists())
            return json.loads((out / "feed_research.json").read_text(encoding="utf-8"))

    def test_compare_drafts_outputs_files_and_boundary(self) -> None:
        audit = self.run_lab(
            [
                "--audience",
                "AI builders and creator operators interested in source-backed X algorithm research",
                "--draft",
                "I audited a viral X algorithm claim against public source. Verdict: misleading. What claim should I check next?",
                "--draft",
                "Guaranteed reach boost hack: links and replies will make this go viral https://example.com",
            ]
        )

        self.assertIn("does not predict reach", audit["boundary"])
        self.assertEqual(audit["best_draft_id"], "draft_1")
        self.assertTrue(any("prediction/boost/shadowban" in warning for warning in audit["warnings"]))
        self.assertTrue(any("link-friction" in warning for warning in audit["warnings"]))

    def test_custom_personas_file_limits_reactions_to_supplied_personas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            personas = Path(tmp) / "personas.json"
            personas.write_text(
                json.dumps(
                    [
                        {
                            "name": "Trust Lead",
                            "segment": "brand safety",
                            "interests": ["safety", "evidence", "policy"],
                            "dislikes": ["guarantee"],
                            "reply_bias": 0.4,
                            "skepticism": 0.8,
                            "link_sensitivity": 0.4,
                            "safety_strictness": 0.9,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            audit = self.run_lab(
                [
                    "--personas-file",
                    str(personas),
                    "--draft",
                    "A source-backed policy audit is safer than claiming a guaranteed algorithm boost.",
                ]
            )

        self.assertEqual(len(audit["personas"]), 1)
        self.assertEqual(audit["personas"][0]["name"], "Trust Lead")
        self.assertEqual(len(audit["reactions"]), 1)
        self.assertEqual(audit["reactions"][0]["persona"], "Trust Lead")

    def test_drafts_file_plain_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts.txt"
            drafts.write_text(
                "First draft asks a clear question about public evidence.\n---\nSecond draft uses a sharper reply hook.",
                encoding="utf-8",
            )
            audit = self.run_lab(["--drafts-file", str(drafts)])

        self.assertEqual(len(audit["drafts"]), 2)
        self.assertEqual(set(audit["draft_summary"].keys()), {"draft_1", "draft_2"})


if __name__ == "__main__":
    unittest.main()
