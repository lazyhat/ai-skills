# Behavioral skill evals

These opt-in evaluations run realistic requests through `codex exec` in disposable Git repositories. They grade
observable behavior rather than checking whether an answer mentions a skill name.

## Safety and cost

Each subject receives a fresh temporary checkout and no additional writable root from the harness. Runs are ephemeral
and use the `workspace-write` sandbox with approvals disabled. Common network and build commands are replaced with
failing logging stubs unless a scenario supplies a safe response. Fixtures must never contain credentials, user data,
or links to a live working checkout.

Every subject or judge invocation consumes a normal model request. Nothing runs automatically in CI.

## Run

Run the deterministic checks and leave semantic decisions for review:

```bash
./evals/run.py --scenario localized-fix
```

Run the semantic rubric through an independent second Codex invocation:

```bash
./evals/run.py --scenario localized-fix --judge
```

Omit `--scenario` to run the complete suite. Use `--model <model>` only when comparing a deliberate model target.
Results are written under the ignored `evals/results/` directory. Add `--keep-worktrees` only when a failed run needs
artifact inspection.

Exit codes are part of the contract:

- `0`: every selected scenario passed, including semantic rubrics;
- `1`: execution, deterministic evidence, or semantic judgment failed;
- `2`: deterministic evidence passed, but at least one semantic rubric still needs human or model review.

## Scenario contract

Each `evals/scenarios/<id>/` contains `scenario.json` and a `fixture/` source tree. Assertions may check logged stub
commands, their order and counts, paths, file contents, verification commands, commit count, and worktree cleanliness.
Unknown assertion names are rejected so a typo cannot silently weaken a scenario.

Use deterministic assertions for machine-observable contracts. Put design judgment, quality of questions, scope, and
truthfulness of claims in `rubric`. A rubric scenario cannot report `PASS` unless `--judge` is used; otherwise it is
explicitly `NEEDS_REVIEW`.

Keep scenarios realistic but narrow. Do not assert exact prose, private reasoning, or the presence of a skill name.
