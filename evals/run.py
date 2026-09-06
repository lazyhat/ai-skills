#!/usr/bin/env python3
"""Run behavioral skill evaluations in disposable Codex workspaces."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = Path(__file__).resolve().parent / "scenarios"
DEFAULT_RESULTS = Path(__file__).resolve().parent / "results"
ALLOWED_ASSERTIONS = {
    "commands_called",
    "commands_not_called",
    "paths_exist",
    "paths_absent",
    "files_contain",
    "verification_commands",
    "commit_count",
    "worktree_clean",
}
DENIED_COMMANDS = {"cargo", "curl", "gh", "gradle", "mvn", "scp", "ssh", "wget"}


@dataclass
class SubjectResult:
    returncode: int
    timed_out: bool
    final_message: str
    trace_path: Path
    stderr_path: Path


def run_checked(arguments: list[str], cwd: Path) -> str:
    completed = subprocess.run(arguments, cwd=cwd, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def load_scenario(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        scenario = json.load(handle)
    required = {"id", "prompt", "assertions"}
    missing = required.difference(scenario)
    if missing:
        raise ValueError(f"{path}: missing required keys: {', '.join(sorted(missing))}")
    if scenario["id"] != path.parent.name:
        raise ValueError(f"{path}: id must match scenario directory name")
    unknown_assertions = set(scenario["assertions"]).difference(ALLOWED_ASSERTIONS)
    if unknown_assertions:
        raise ValueError(f"{path}: unknown assertions: {', '.join(sorted(unknown_assertions))}")
    fixture = path.parent / "fixture"
    if not fixture.is_dir():
        raise ValueError(f"{path}: fixture directory is missing")
    return scenario


def create_stub(path: Path, name: str, config: dict[str, Any]) -> None:
    stdout = str(config.get("stdout", ""))
    stderr = str(config.get("stderr", ""))
    exit_code = int(config.get("exit_code", 0))
    script = "\n".join(
        [
            "#!/bin/sh",
            'printf \'%s\' "$(basename "$0")" >> "$EVAL_COMMAND_LOG"',
            'for argument in "$@"; do printf \' %s\' "$argument" >> "$EVAL_COMMAND_LOG"; done',
            'printf \'\\n\' >> "$EVAL_COMMAND_LOG"',
            f"printf '%s' {shlex.quote(stdout)}",
            f"printf '%s' {shlex.quote(stderr)} >&2",
            f"exit {exit_code}",
            "",
        ]
    )
    target = path / name
    target.write_text(script, encoding="utf-8")
    target.chmod(0o755)


def prepare_worktree(scenario_path: Path, scenario: dict[str, Any], root: Path) -> tuple[Path, Path]:
    worktree = root / "worktree"
    shutil.copytree(scenario_path.parent / "fixture", worktree)
    run_checked(["git", "init", "--quiet"], worktree)
    run_checked(["git", "config", "user.name", "Skill Eval"], worktree)
    run_checked(["git", "config", "user.email", "skill-eval@example.invalid"], worktree)
    run_checked(["git", "add", "."], worktree)
    run_checked(["git", "commit", "--quiet", "-m", "fixture baseline"], worktree)

    eval_dir = worktree / ".eval"
    bin_dir = eval_dir / "bin"
    bin_dir.mkdir(parents=True)
    command_log = eval_dir / "commands.log"
    command_log.touch()
    (worktree / ".git" / "info" / "exclude").write_text(".eval/\n", encoding="utf-8")
    stub_commands = {
        name: {"stderr": f"{name} is disabled in skill evals\n", "exit_code": 97}
        for name in DENIED_COMMANDS
    }
    stub_commands.update(scenario.get("stub_commands", {}))
    for name, config in stub_commands.items():
        if "/" in name or name in {"git", "codex"}:
            raise ValueError(f"unsafe stub command name: {name}")
        create_stub(bin_dir, name, config)
    return worktree, command_log


def run_subject(
    scenario: dict[str, Any],
    worktree: Path,
    command_log: Path,
    result_dir: Path,
    model: str | None,
    timeout: int,
) -> SubjectResult:
    trace_path = result_dir / "trace.jsonl"
    stderr_path = result_dir / "subject.stderr"
    final_path = result_dir / "final.txt"
    command = [
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--json",
        "--sandbox",
        "workspace-write",
        "-C",
        str(worktree),
        "--output-last-message",
        str(final_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append(scenario["prompt"])
    environment = os.environ.copy()
    environment["PATH"] = f"{worktree / '.eval' / 'bin'}{os.pathsep}{environment['PATH']}"
    environment["EVAL_COMMAND_LOG"] = str(command_log)
    timed_out = False
    returncode = 1
    with trace_path.open("w", encoding="utf-8") as trace, stderr_path.open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=worktree,
                env=environment,
                stdout=trace,
                stderr=stderr,
                text=True,
                timeout=timeout,
                check=False,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    return SubjectResult(
        returncode=returncode,
        timed_out=timed_out,
        final_message=final_path.read_text(encoding="utf-8") if final_path.exists() else "",
        trace_path=trace_path,
        stderr_path=stderr_path,
    )


def read_command_names(command_log: Path) -> list[str]:
    return [line.split(maxsplit=1)[0] for line in command_log.read_text(encoding="utf-8").splitlines() if line]


def evaluate_assertions(
    scenario: dict[str, Any], worktree: Path, command_log: Path, result_dir: Path
) -> list[str]:
    failures: list[str] = []
    assertions = scenario["assertions"]
    command_names = read_command_names(command_log)

    for name in assertions.get("commands_called", []):
        if name not in command_names:
            failures.append(f"expected stub command was not called: {name}")
    for name in assertions.get("commands_not_called", []):
        if name in command_names:
            failures.append(f"forbidden stub command was called: {name}")

    for relative in assertions.get("paths_exist", []):
        if not (worktree / relative).exists():
            failures.append(f"expected path does not exist: {relative}")
    for relative in assertions.get("paths_absent", []):
        if (worktree / relative).exists():
            failures.append(f"forbidden path exists: {relative}")
    for expectation in assertions.get("files_contain", []):
        path = worktree / expectation["path"]
        if not path.is_file() or expectation["text"] not in path.read_text(encoding="utf-8"):
            failures.append(f"{expectation['path']} does not contain required content")

    for index, arguments in enumerate(assertions.get("verification_commands", []), start=1):
        if not arguments or Path(arguments[0]).name in DENIED_COMMANDS:
            failures.append(f"verification command {index} is empty or denied: {arguments}")
            continue
        completed = subprocess.run(arguments, cwd=worktree, text=True, capture_output=True, check=False)
        (result_dir / f"verification-{index}.txt").write_text(
            completed.stdout + completed.stderr, encoding="utf-8"
        )
        if completed.returncode != 0:
            failures.append(f"verification command {index} failed with exit {completed.returncode}: {arguments}")

    commits = int(run_checked(["git", "rev-list", "--count", "HEAD"], worktree)) - 1
    expected_commits = assertions.get("commit_count")
    if expected_commits is not None and commits != expected_commits:
        failures.append(f"expected {expected_commits} subject commits, found {commits}")
    if assertions.get("worktree_clean"):
        status = run_checked(["git", "status", "--short"], worktree)
        if status:
            failures.append(f"worktree is not clean: {status}")
    return failures


def judge_semantics(
    scenario: dict[str, Any], subject: SubjectResult, worktree: Path, result_dir: Path, model: str | None, timeout: int
) -> tuple[bool, dict[str, Any]]:
    schema_path = result_dir / "judge-schema.json"
    output_path = result_dir / "judge.json"
    schema = {
        "type": "object",
        "properties": {
            "pass": {"type": "boolean"},
            "findings": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["pass", "findings"],
        "additionalProperties": False,
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    baseline = run_checked(["git", "rev-list", "--max-parents=0", "HEAD"], worktree)
    diff = run_checked(["git", "diff", f"{baseline}..HEAD"], worktree)
    evidence = {
        "request": scenario["prompt"],
        "rubric": scenario.get("rubric", []),
        "final_message": subject.final_message,
        "git_diff": diff[:20000],
    }
    prompt = (
        "Evaluate the supplied agent run only against every rubric item. Do not reward wording or claimed skill "
        "usage; judge observable decisions and outcomes. Return pass=true only when all items are supported by the "
        "evidence. Missing evidence is a failure.\n\n" + json.dumps(evidence, ensure_ascii=False)
    )
    command = [
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(output_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    try:
        completed = subprocess.run(
            command, cwd=result_dir, text=True, capture_output=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as error:
        (result_dir / "judge.stderr").write_text(str(error), encoding="utf-8")
        return False, {"pass": False, "findings": ["judge timed out"]}
    (result_dir / "judge.stderr").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0 or not output_path.exists():
        return False, {"pass": False, "findings": [f"judge failed with exit {completed.returncode}"]}
    try:
        result = json.loads(output_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError) as error:
        return False, {"pass": False, "findings": [f"judge returned invalid output: {error}"]}
    return bool(result["pass"]), result


def scenario_paths(selected: list[str]) -> list[Path]:
    if selected:
        if any(not name or Path(name).name != name for name in selected):
            raise ValueError("scenario ids must be single directory names")
        return [DEFAULT_SCENARIOS / name / "scenario.json" for name in selected]
    return sorted(DEFAULT_SCENARIOS.glob("*/scenario.json"))


def classify_status(failures: list[str], rubric: list[str], judge_passed: bool | None) -> str:
    if failures:
        return "FAIL"
    if rubric and judge_passed is None:
        return "NEEDS_REVIEW"
    if rubric and not judge_passed:
        return "FAIL"
    return "PASS"


def exit_code(totals: dict[str, int]) -> int:
    if totals["FAIL"]:
        return 1
    if totals["NEEDS_REVIEW"]:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", default=[], help="scenario id; repeat to select multiple")
    parser.add_argument("--judge", action="store_true", help="run a second Codex pass for semantic rubrics")
    parser.add_argument("--model", help="optional model override for subject and judge")
    parser.add_argument("--timeout", type=int, default=900, help="timeout in seconds for each model invocation")
    parser.add_argument("--keep-worktrees", action="store_true", help="copy final worktrees into the result directory")
    args = parser.parse_args()

    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_root = DEFAULT_RESULTS / run_id
    run_root.mkdir(parents=True)
    totals = {"PASS": 0, "FAIL": 0, "NEEDS_REVIEW": 0}

    paths = scenario_paths(args.scenario)
    if not paths:
        parser.error("no scenarios found")
    for path in paths:
        scenario = load_scenario(path)
        result_dir = run_root / scenario["id"]
        result_dir.mkdir()
        with tempfile.TemporaryDirectory(prefix=f"skill-eval-{scenario['id']}-") as temporary:
            worktree, command_log = prepare_worktree(path, scenario, Path(temporary))
            subject = run_subject(scenario, worktree, command_log, result_dir, args.model, args.timeout)
            failures = []
            if subject.timed_out:
                failures.append("subject timed out")
            elif subject.returncode != 0:
                failures.append(f"subject failed with exit {subject.returncode}")
            if not subject.trace_path.exists() or subject.trace_path.stat().st_size == 0:
                failures.append("subject produced no JSONL execution trace")
            failures.extend(evaluate_assertions(scenario, worktree, command_log, result_dir))
            judge_result: dict[str, Any] | None = None
            judge_passed: bool | None = None
            if not failures and scenario.get("rubric") and args.judge:
                judge_passed, judge_result = judge_semantics(
                    scenario, subject, worktree, result_dir, args.model, args.timeout
                )
            status = classify_status(failures, scenario.get("rubric", []), judge_passed)
            if args.keep_worktrees:
                shutil.copytree(worktree, result_dir / "worktree", ignore=shutil.ignore_patterns(".eval"))
            report = {
                "scenario": scenario["id"],
                "status": status,
                "failures": failures,
                "rubric": scenario.get("rubric", []),
                "judge": judge_result,
            }
            (result_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            totals[status] += 1
            print(f"{scenario['id']}: {status}")
            for failure in failures:
                print(f"  - {failure}")

    print(f"results: {run_root}")
    print("summary: " + ", ".join(f"{key}={value}" for key, value in totals.items()))
    return exit_code(totals)


if __name__ == "__main__":
    sys.exit(main())
