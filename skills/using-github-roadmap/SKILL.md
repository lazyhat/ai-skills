---
name: using-github-roadmap
description: Use when starting feature work, bugfix, or idea capture in a repo that tracks work on a GitHub Projects v2 Roadmap board - binds each unit of work to a tracked issue before brainstorming, planning, executing, or finishing.
---

# Using a GitHub Roadmap

## Overview

All non-trivial work in a roadmap-tracked repo MUST be bound to a GitHub issue that lives on the project board. This skill is the single source of truth for the `gh` commands and the workflow that brainstorming, writing-plans, executing-plans, and finishing-a-development-branch hook into.

**Announce at start:** "I'm using the using-github-roadmap skill to bind this work to the roadmap."

<HARD-GATE>
Do NOT continue with brainstorming, writing-plans, executing-plans, or finishing-a-development-branch until the current unit of work has an associated GitHub issue and that issue is on the roadmap project. If no project config is present in the repo, stop and ask the user to add one (template in the "Per-repo config" section).
</HARD-GATE>

## When to Use

- Starting any feature, bugfix, refactor, or chore that will produce a commit.
- Capturing a new idea that the user wants to remember.
- Resuming work on a partially-implemented spec/plan.
- Before invoking brainstorming, writing-plans, executing-plans, or finishing-a-development-branch.

**Do NOT use for:** one-off shell/terminal questions, reading code, answering questions that produce no commits.

## Per-repo config

Skill reads `.github/copilot-instructions.md` from the active repo and looks for a fenced block tagged `roadmap`:

````markdown
```yaml roadmap
owner: <github-user-or-org>
repo: <owner/name>
project_number: <N>
project_id: <PVT_xxx>          # gh project view N --owner <owner> --format json
status_field_id: <PVTSSF_xxx>  # gh project field-list N --owner <owner> --format json
statuses:
  Inbox: <option-id>
  Backlog: <option-id>
  Next: <option-id>
  Now: <option-id>
  Done: <option-id>
  Dropped: <option-id>
```
````

If the block is missing or incomplete, stop and ask the user to add it. Print the template above verbatim.

## Operations

### `roadmap:select-or-create`

Used at the start of brainstorming, writing-plans, or executing-plans.

1. List active issues on the board:
   ```bash
   gh project item-list <N> --owner <owner> --limit 50 --format json \
     --jq '.items[] | select(.status == "Now" or .status == "Next" or .status == "Backlog" or .status == "Inbox") | "#\(.content.number) [\(.status)] \(.content.title)"'
   ```
2. Match the current unit of work against candidate issues strictly:
   - Use an existing issue only when its title/body match the current deliverable 1:1.
   - Do not bind work to a broad, adjacent, or merely related issue just because it is close.
   - If a candidate is related but not exact, run `roadmap:related-issue-triage` before selecting or creating anything.
3. Present a `vscode_askQuestions` with exact-match issues, related-but-not-exact issues clearly marked, "Create new issue", and "Skip (work without issue, requires explicit user override)".
4. If create:
   - Ask for title, theme label (one of repo's `theme:*`), optional `priority:*`, `kind:idea` for umbrella.
   - Write a detailed issue body using `roadmap:issue-body-template`.
   - `gh issue create --repo <repo> --title "<title>" --label "<labels>" --body "<body>"` → capture URL.
   - `gh project item-add <N> --owner <owner> --url <URL> --format json --jq .id` → capture item id.
   - Set Status = Inbox via `roadmap:status`.
5. Return `{issue_number, issue_url, item_id}`.

### `roadmap:issue-body-template`

New issues created during execution must be useful without the chat transcript. Do not create one-line placeholder issues.

Use this Markdown body:

```markdown
## Context

<Why this work exists now. Include the user-visible problem, current code state, and any related issue numbers.>

## Goal

<One concrete outcome this issue should deliver.>

## Scope

- <Specific change 1>
- <Specific change 2>
- <Specific change 3>

## Out of Scope

- <Explicitly excluded adjacent work>
- <Architecture/feature work that should not sneak into this issue>

## Acceptance Criteria

- [ ] <Observable behavior or code boundary that must be true>
- [ ] <Compatibility/API behavior that must remain true>
- [ ] <User-facing or developer-facing result>

## Verification

- <Exact command/test/manual check expected for this issue>
- <Additional command/test/manual check if needed>

## Links

- Related: #<n>
- Parent/Sub-task: #<n>
```

Rules:
- If there are no related issues, omit the `Links` section.
- `Acceptance Criteria` must be specific enough that a reviewer can decide whether the issue is done.
- `Verification` must name concrete commands or concrete in-game/manual checks.
- `Out of Scope` is required when an adjacent issue exists or when the work could easily expand.
- If you cannot fill a section from available context, ask the user before creating the issue.

### `roadmap:related-issue-triage`

Use this when an existing issue is close to the current work but does not match 1:1.

1. Check whether the existing issue is still relevant:
   ```bash
   gh issue view <n> --repo <repo> --json number,title,body,state,labels,url
   ```
   - If the issue is obsolete or no longer describes intended work, close it as `not_planned`, set Roadmap Status = Dropped, then create a new exact issue for the current work.
   - If the issue is still relevant, keep it open and create or select a separate exact issue for the current work.
2. Establish the relationship:
   - If the existing issue is broader/umbrella and current work is a slice, make the current issue a sub-issue of the existing one when the repo/project supports GitHub sub-issues.
   - If the current work is broader and the existing issue is a slice, make the existing issue a sub-issue of the current issue when supported.
   - If sub-issues are not available through the configured tooling, add explicit cross-links with issue comments:
     ```bash
     gh issue comment <parent> --repo <repo> --body "Sub-task: #<child>"
     gh issue comment <child> --repo <repo> --body "Parent task: #<parent>"
     ```
   - If neither issue owns the other, link both as related:
     ```bash
     gh issue comment <a> --repo <repo> --body "Related: #<b>"
     gh issue comment <b> --repo <repo> --body "Related: #<a>"
     ```
3. Bind the current session to the exact issue, not to the related issue.
4. If relationship semantics are ambiguous, stop and ask the user before creating links.

### `roadmap:link-spec`

Return the line to embed at the top of any spec/plan:

```markdown
> Issue: [#N](https://github.com/<owner>/<repo>/issues/N)
```

This is the first content line under the `# Title` of every spec and plan generated in a roadmap-tracked repo.

### `roadmap:status <Inbox|Backlog|Next|Now|Done|Dropped> <item-id>`

```bash
gh project item-edit \
  --project-id <project_id> \
  --field-id <status_field_id> \
  --id <item-id> \
  --single-select-option-id <statuses[<status>]>
```

If `item-id` is unknown, resolve it from `issue_number`:

```bash
gh project item-list <N> --owner <owner> --limit 100 --format json \
  --jq ".items[] | select(.content.number == <issue_number>) | .id"
```

### `roadmap:close <issue_number> <completed|not_planned>`

```bash
gh api -X PATCH /repos/<repo>/issues/<n> \
  -f state=closed -f state_reason=<reason>
```

GitHub auto-moves closed items to Done in well-configured boards. Verify and set Status explicitly with `roadmap:status Done` if needed.

## Phase hooks (called by other skills)

| Phase | Caller | Action |
|---|---|---|
| Pre-brainstorm | brainstorming step 0 | `select-or-create` → return `#N` |
| Spec header | brainstorming step 6 | `link-spec` → embed line in spec |
| Plan header | writing-plans header section | `link-spec` → embed line in plan |
| Pre-execute | executing-plans step 1.5 | `status Now` |
| Post-execute | executing-plans step 3 | `status Done` (or `close completed`) |
| Branch finish | finishing-a-development-branch end | `close <reason>` |

## Common Mistakes

- **Heredoc inside `&&` chain in zsh.** `cat > f << EOF ... EOF && cmd` puts zsh into `cmdand heredoc>` continuation hell. Always run heredocs as standalone commands, or use `--body-file` with a file written via your editor's file-write tool.
- **fine-grained PAT for user-owned Projects v2.** GitHub explicitly does not support this. For roadmap operations a classic PAT with scope `project` is required. Repo-only issue operations work via REST PATCH on fine-grained tokens but `addComment`, `closeIssue`, and `createProjectV2` GraphQL mutations do not.
- **Forgetting to add the issue to the project.** `gh issue create` does NOT auto-add to a project. Always follow with `gh project item-add`.
- **Filename collisions when bound to issue.** Keep spec/plan filenames date-based; put `Issue: #N` in the header, not the filename.
- **Skipping the gate "because it's a small change".** If the change produces a commit on `dev`/`main`, it needs an issue. Use a single `chore: ...` issue if you must.

## Quick Reference

```bash
# Active board (Roadmap)
gh project item-list 6 --owner lazyhat --limit 50 --format json \
  --jq '.items[] | "\(.content.number) [\(.status)] \(.content.title)"'

# New issue + onto board
URL=$(gh issue create --repo lazyhat/Compukter-Kraft --title "..." --label "theme:language" --body "...")
ITEM=$(gh project item-add 6 --owner lazyhat --url "$URL" --format json --jq .id)

# Move to Now
gh project item-edit --project-id PVT_kwHOBkSydc4BYgqn \
  --field-id PVTSSF_lAHOBkSydc4BYgqnzhTmClk \
  --id "$ITEM" --single-select-option-id 0ea1b704

# Close
N=$(echo "$URL" | awk -F/ '{print $NF}')
gh api -X PATCH /repos/lazyhat/Compukter-Kraft/issues/$N \
  -f state=closed -f state_reason=completed
```

## Integration

- **brainstorming** → calls `select-or-create` at step 0, `link-spec` at spec write.
- **writing-plans** → requires `Issue: #N` header line.
- **executing-plans** → calls `status Now` before first task, `status Done` after last.
- **finishing-a-development-branch** → calls `close` after integration.
