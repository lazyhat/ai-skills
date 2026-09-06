import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("skill_eval_run", Path(__file__).parents[1] / "run.py")
RUN = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = RUN
SPEC.loader.exec_module(RUN)


class SkillEvalHarnessTest(unittest.TestCase):
    def test_repository_scenarios_are_valid(self):
        paths = sorted((Path(__file__).parents[1] / "scenarios").glob("*/scenario.json"))

        self.assertEqual(6, len(paths))
        for path in paths:
            with self.subTest(path=path):
                RUN.load_scenario(path)

    def test_load_scenario_requires_matching_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            scenario_dir = Path(temporary) / "example"
            (scenario_dir / "fixture").mkdir(parents=True)
            scenario_path = scenario_dir / "scenario.json"
            scenario_path.write_text(
                json.dumps({"id": "example", "prompt": "Do work", "assertions": {}}), encoding="utf-8"
            )

            loaded = RUN.load_scenario(scenario_path)

            self.assertEqual("example", loaded["id"])

    def test_load_scenario_rejects_unknown_assertion(self):
        with tempfile.TemporaryDirectory() as temporary:
            scenario_dir = Path(temporary) / "example"
            (scenario_dir / "fixture").mkdir(parents=True)
            scenario_path = scenario_dir / "scenario.json"
            scenario_path.write_text(
                json.dumps({"id": "example", "prompt": "Do work", "assertions": {"typo": True}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unknown assertions: typo"):
                RUN.load_scenario(scenario_path)

    def test_deterministic_assertions_check_behavior_and_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scenario_dir = root / "example"
            fixture = scenario_dir / "fixture"
            fixture.mkdir(parents=True)
            (fixture / "value.txt").write_text("before\n", encoding="utf-8")
            (fixture / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            scenario = {
                "id": "example",
                "prompt": "Change the value",
                "assertions": {
                    "commands_called": ["verify"],
                    "commands_not_called": ["gh"],
                    "command_counts": {"verify": 1},
                    "commands_in_order": ["verify"],
                    "files_contain": [{"path": "value.txt", "text": "after"}],
                    "verification_commands": [["python3", "-c", "import module"]],
                    "commit_count": 1,
                    "worktree_clean": True,
                },
                "stub_commands": {"verify": {}},
            }
            worktree, command_log = RUN.prepare_worktree(scenario_dir / "scenario.json", scenario, root / "run")
            (worktree / "value.txt").write_text("after\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["EVAL_COMMAND_LOG"] = str(command_log)
            subprocess.run(
                [str(worktree / ".eval" / "bin" / "verify")],
                cwd=worktree,
                env=environment,
                check=True,
            )
            RUN.run_checked(["git", "add", "value.txt"], worktree)
            RUN.run_checked(["git", "commit", "--quiet", "-m", "change value"], worktree)

            failures = RUN.evaluate_assertions(scenario, worktree, command_log, root)

            self.assertEqual([], failures)

    def test_deterministic_assertions_report_missing_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scenario_dir = root / "example"
            fixture = scenario_dir / "fixture"
            fixture.mkdir(parents=True)
            (fixture / "value.txt").write_text("before\n", encoding="utf-8")
            scenario = {
                "id": "example",
                "prompt": "Change the value",
                "assertions": {"commands_called": ["verify"], "commit_count": 1},
            }
            worktree, command_log = RUN.prepare_worktree(scenario_dir / "scenario.json", scenario, root / "run")

            failures = RUN.evaluate_assertions(scenario, worktree, command_log, root)

            self.assertIn("expected stub command was not called: verify", failures)
            self.assertIn("expected 1 subject commits, found 0", failures)

    def test_semantic_rubric_never_passes_without_review(self):
        self.assertEqual("NEEDS_REVIEW", RUN.classify_status([], ["Ask about ownership"], None))
        self.assertEqual(2, RUN.exit_code({"PASS": 1, "FAIL": 0, "NEEDS_REVIEW": 1}))

    def test_execution_evidence_keeps_completed_commands(self):
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / "trace.jsonl"
            trace.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "turn.started"}),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "command_execution",
                                    "command": "./verify",
                                    "exit_code": 0,
                                    "aggregated_output": "all tests passed",
                                },
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                [{"command": "./verify", "exit_code": 0, "output": "all tests passed"}],
                RUN.execution_evidence(trace),
            )

    def test_failures_override_semantic_judgment(self):
        self.assertEqual("FAIL", RUN.classify_status(["missing test"], ["Ask a question"], True))
        self.assertEqual(1, RUN.exit_code({"PASS": 0, "FAIL": 1, "NEEDS_REVIEW": 0}))


if __name__ == "__main__":
    unittest.main()
