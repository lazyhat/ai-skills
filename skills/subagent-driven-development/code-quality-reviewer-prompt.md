# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Task tool (superpowers:code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]
```

**In addition to standard code quality concerns, the reviewer should check:**
- Does each file have one clear responsibility with a well-defined interface?
- Are units decomposed so they can be understood and tested independently?
- Is the implementation following the file structure from the plan?
- Did this implementation create new files that are already large, or significantly grow existing files? (Don't flag pre-existing file sizes — focus on what this change contributed.)
- If the task text or plan context is internally inconsistent, impossible to satisfy as written, or contradicts what spec review already established, stop and report `PLAN_MISMATCH` instead of guessing what "good" means.

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

**Assessment values:**
- `APPROVED` - implementation is well-built for the reviewed task
- `CHANGES_REQUESTED` - code quality issues need fixes before approval
- `PLAN_MISMATCH` - the task or plan is not coherent enough to judge implementation quality reliably; controller should ask the human via VS Code askQuestions
