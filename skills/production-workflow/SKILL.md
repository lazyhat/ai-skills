---
name: production-workflow
description: Use when starting or resuming changes in a software repository, including implementation, bug fixes, refactors, plans, documentation, configuration, or when the user reports making a change and asks to continue.
---

# Production Workflow

Route repository work through the relevant specialist skills while preserving momentum, user changes,
and repository policy.

## Establish State

Read applicable repository instructions and inspect enough current state to identify the next incomplete
step. Preserve user changes and do not redo completed work. A direct request to implement or fix something
authorizes ordinary in-scope changes; ask only when a material choice, missing authority, or conflicting
state prevents safe progress.

## Isolate Implementation Work

For repository changes, use a separate Git worktree and task branch by default. Read-only investigation
can stay in the current checkout. Reuse an existing worktree for the same task rather than creating
another one. Record the starting commit, preserve the original checkout and its user changes, and keep
all task edits, checks, and commits in the task worktree. Initialize required submodules at the revisions
pinned by that checkout; do not copy another agent's uncommitted state. Follow repository conventions
for worktree locations. Merge only with current or standing user authorization; do not push or remove
the worktree without authorization.

Explicit user instructions and repository checkout rules override this default. A repository instruction
to stay in the current checkout applies unless the user explicitly requests a worktree for this task.

## Compukters Checkout Preparation

For Compukters repository changes, use the workspace `worktree-task` command by default before editing.
Read-only investigation may remain in the current checkout. Reuse a worktree only for the same active task;
start a new task from current local `dev`, or local `main` for a submodule. Follow explicit user checkout
instructions when they override this default.

```sh
./worktree-task feat/display-api
./worktree-task feat/create-support --submodule addons/create
./worktree-task fix/vm-execution --repo host/compukter-vm
```

The first command creates the parent task checkout, initializes the pinned VM, and prepares an independent
Gradle cache. Addons are opt-in: select required addons with repeatable `--submodule` options before editing;
use `--all-submodules` only when the task needs all of them. Use `--no-submodules` for tasks needing none.
`--repo` selects an already initialized submodule repository and starts its task branch from local `main`.
When a task changes both parent and submodule code, prepare a parent task checkout as well so the resulting
submodule pin can be committed there.

Run setup outside the sandbox because submodule preparation may access remotes. If the current checkout
lacks the helper, invoke `worktree-task` by its absolute path in the main Compukters workspace. Enter the
printed checkout, verify its branch and starting commit, and keep task edits, checks, and commits there.
Run `./worktree-task doctor` before the first build, or use the main entrypoint with `doctor --path <checkout>`.
Resolve reported prerequisite errors before building; a cold cache is informational and does not prove offline readiness.
Do not replace the helper with manual `git worktree add` or cache copies when it is available. It does not
fetch or pull the base branch; do not add an unsolicited remote update.

If setup fails after creation, preserve the reported checkout and branch. Fix the cause and repeat the
same command from the main workspace entrypoint with `--resume` only while that registered task checkout
is clean; do not invoke resume from inside the checkout it is preparing. After edits, preserve them
and finish remaining setup manually; do not recreate or reset the checkout. Never adopt another task's
branch or destination to bypass an existing-path error.

Use sandbox Gradle wrappers for builds: they manage independent copy-on-write cache homes, including cold
initialization. Never copy caches manually, hard-link cache files, or share writable homes through symlinks.
For options and recovery details, read `docs/contributors/development.md` and the Gradle-cache section of
`docs/contributors/verification.md` in the workspace. Completion follows the policy below.

## Verify Git Identity

Before the first task commit, and again after creating or switching a worktree or checkout, inspect
`git config --show-origin --get user.name`, `git config --show-origin --get user.email`,
`git var GIT_AUTHOR_IDENT`, and `git var GIT_COMMITTER_IDENT` in the actual working checkout. Environment
variables can override configured identity. Use the user's established repository identity for both author
and committer; do not invent an agent identity or rely on `--author` alone. Resolve unexpected differences
before committing, without changing global Git configuration. Repeat this check for separately committed
submodules and verify the recorded author/committer after the commit.

## Preserve Architectural Integrity

Do not silently trade architectural correctness for speed. A workaround is not an acceptable default when it knowingly
preserves incorrect ownership or component boundaries, duplicates a source of truth, bypasses an intended abstraction
or invariant, or special-cases a symptom while leaving its structural cause in place.

When a task presents a real choice between a durable architectural correction and a quicker compromise of that kind,
stop before implementation. Explain the durable option, the expedient option, and their concrete scope and
consequences, then ask the user which direction to take. Do not implement the compromise without explicit user
approval, even when it is smaller or reversible. This gate does not apply merely because a correct localized fix is
small; use it when speed and architectural integrity actually conflict.

## User-Reported Changes

When the user says they changed, fixed, installed, merged, configured, or verified something and asks to
continue:

1. Treat the report as a state transition to verify, not as work to repeat.
2. Inspect the narrowest relevant evidence: file content or diff, effective configuration, dependency
   version and lockfile, focused reproduction or test, build artifact, or remote state through the
   repository-approved tool.
3. If evidence matches the expected state, continue from the next incomplete step.
4. If the only defect is formatting with no semantic effect, repair it and continue without asking.
5. If the change is missing, functionally incorrect, semantically different from the agreed model, or
   invalidates the current plan, stop dependent work. Report expected versus observed evidence and ask
   the user how to proceed.
6. If objective verification is unavailable, state what remains unverified. Continue only when the
   assumption is low-risk; otherwise request the necessary evidence or access.

Do not second-guess subjective manual results without contrary evidence. Verify any related machine state
that is accessible.

## Route the Work

- For a bug, failing test, build failure, performance regression, or unexpected behavior, use
  `debugging-strategy` before proposing or implementing a fix.
- For explicit ideation or unresolved product, architecture, public-interface, or scope decisions, use
  `brainstorming`. For architecturally significant work in a roadmap-tracked repository, first use
  `using-github-roadmap` as required by repository policy, then continue with `brainstorming`.
- For an accepted design or requirements that need coordinated implementation stages, use
  `writing-plans`. When resuming an existing plan, use `executing-plans`.
- Before changing production behavior, use `testing-strategy` to choose proportional evidence and whether
  test-first is valuable. Documentation, formatting, and non-executable configuration normally use direct
  validation rather than automated tests unless repository policy says otherwise.
- When acting on code-review feedback, use `review-feedback`.

Before claiming completion, committing, or handing work back, use
`verification-workflow`. For a localized task, run proportional checks, create one
focused commit, and apply any authorized completion policy below. For a multi-stage plan, run focused
verification and create a coherent commit
after each completed stage; after every stage is complete, run the repository's full verification and
apply any authorized completion policy below. Otherwise stop after verification. Do not push or open a
pull request unless the user explicitly requests it; a local merge does not authorize either action.

Repository and user instructions override workflow preferences, including artifact locations, issue
tracking, worktrees, delegation, commits, remote operations, and verification commands.

## Compukters Completion Policy

For the Compukters workspace, the user has given standing authorization to merge verified task work
before declaring it complete: merge the main repository task branch into `dev`, and merge task work
inside its Git submodules into their `main` branches. Do not ask for merge permission again unless a
new user instruction overrides this default or conflicting state makes integration unsafe.

Keep implementation isolated in its task worktree. Before merging, inspect the destination checkout,
preserve unrelated user changes, and complete the relevant verification. If a task changes a submodule,
merge its work into `main` first, then record the resulting pinned commit in the parent task branch
and integrate that branch into `dev`. Verify the integrated commit with checks proportional to the
change and report the merge result before finishing. Do not discard unrelated submodule checkout
changes or update their pins as part of an unrelated task.

An explicit request to leave work on its task branch overrides this completion default. This standing
authorization covers local merges and removal of the completed task's worktree after integrated verification;
pushing and opening pull requests still require their own authorization. Before removal, retain verification logs
or other completion evidence outside that worktree, confirm its changes are committed and integrated, and preserve
any unrelated files or user changes. Use the main workspace entrypoint `./worktree-task finish <task-branch>`
from outside the checkout being removed, with `--repo <submodule-path>` for submodule tasks. Keep real verification
output in `build/agent-logs` or supply repeatable `--evidence <path>` options. The helper checks integration and
cleanliness, archives evidence and ignored non-build files, and keeps the branch. It performs no merge or verification
itself. A refusal means preserve the checkout and resolve the stated condition; never bypass it by force-removing a
dirty checkout. Git's required force flag for clean submodule-containing worktrees is handled by the helper only after
its preservation checks. For an older helper checkout without a task record, explicitly register its clean
checkout with the original setup command and `--resume` through the main workspace entrypoint before finishing.
Do not prune unrelated worktrees. Remove only worktrees created for the completed task. Start the next task in
a fresh worktree from current `dev` (or submodule `main`); reuse a checkout only for the same active task.
