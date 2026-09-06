---
name: executing-plans
description: Use when an accepted written implementation plan is ready to execute or resume in the current repository.
---

# Executing Plans

Complete an accepted plan while adapting it to verified repository state.

## Resume from Evidence

Read applicable repository instructions, the plan, linked design or issue, and enough current state to
identify completed and remaining work. Work in the user's current checkout unless explicitly instructed
otherwise. Preserve user changes and do not redo completed tasks.

Review the plan against reality before relying on it. Correct small stale paths, ordering details, and
other mechanical gaps in place. Stop dependent work and ask the user only when evidence reveals a
material design conflict, scope change, missing authority, or blocker. When the user reports making a
change and asks to continue, follow the verification and stopping rules in `production-workflow`.

## Execute to Completion

Implement all remaining tasks in dependency order. Keep plan status current when it helps later
resumption, but do not create arbitrary batch checkpoints or pause for routine deviations.

- For production behavior, use `testing-strategy`.
- For failures or unexpected behavior, use `superpowers:systematic-debugging`.
- Verify meaningful stages with focused checks and the final outcome with
  `superpowers:verification-before-completion`.

Use verification proportional to risk and record any checks that cannot be run. Commit only when user or
repository instructions call for it. If the implementation is complete and branch integration remains a
decision, use `superpowers:finishing-a-development-branch`.
