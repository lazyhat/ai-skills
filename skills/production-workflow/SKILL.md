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
  `superpowers:systematic-debugging` before proposing or implementing a fix.
- For explicit ideation or unresolved product, architecture, public-interface, or scope decisions, use
  `brainstorming`. For architecturally significant work in a roadmap-tracked repository, first use
  `using-github-roadmap` as required by repository policy, then continue with `brainstorming`.
- For an accepted design or requirements that need coordinated implementation stages, use
  `superpowers:writing-plans`. When resuming an existing plan, use `superpowers:executing-plans`.
- Before changing production behavior, use `superpowers:test-driven-development`. Documentation,
  formatting, and non-executable configuration do not require TDD unless repository policy says otherwise.
- When acting on code-review feedback, use `superpowers:receiving-code-review`.

Before claiming completion, committing, opening a pull request, or handing work back, use
`superpowers:verification-before-completion` with checks proportional to the change. If implementation is
complete but branch integration remains a decision, use `superpowers:finishing-a-development-branch`.

Repository and user instructions override workflow preferences, including artifact locations, issue
tracking, worktrees, delegation, commits, remote operations, and verification commands.
