---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers:subagent-driven-development instead of this skill.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically before touching code. Check for plan/reality mismatches, not just missing detail.
3. Treat the following as execution blockers until clarified:
	- steps that contradict each other or the stated goal;
	- files, modules, symbols, branches, versions, or loaders that do not exist in the repo;
	- steps whose order is impossible because a later dependency is required earlier;
	- verification commands that cannot prove the requirement they claim to verify;
	- assumptions that would materially change the implementation if answered differently.
4. If you find any blocker or non-trivial concern, batch them into a single `vscode_askQuestions` prompt and wait for the answer before starting. In VS Code this means the structured askQuestions MCP/UI flow, not a plain-text question.
5. If no concerns: Create TodoWrite and proceed

### Step 1.5: Move roadmap issue to Now

In roadmap-tracked repos (those with a `.github/copilot-instructions.md` roadmap block):
- Read `Issue: #N` from the plan header. If missing, invoke superpowers:using-github-roadmap → `select-or-create`.
- REQUIRED SUB-SKILL: superpowers:using-github-roadmap → `status Now`.

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. If repo reality disagrees with the plan while executing, stop that task and use `vscode_askQuestions` before improvising. Examples: renamed APIs, missing files, failing prerequisite steps, or a step that would undo an earlier requirement.
4. Run verifications as specified
5. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- In roadmap-tracked repos: REQUIRED SUB-SKILL: superpowers:using-github-roadmap → `status Done` (or `close <reason>` for trivial work).
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- Plan conflicts with the current codebase or earlier completed tasks
- You don't understand an instruction
- Verification fails repeatedly

**Use `vscode_askQuestions` for clarification rather than guessing. Ask one compact question set that makes the decision explicit.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Validate plan against repo reality before starting and during execution
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers:writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
