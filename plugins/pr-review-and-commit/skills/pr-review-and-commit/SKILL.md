---
name: pr-review-and-commit
description: Explicit GitHub pull-request review and delivery for one or more connected PR URLs. Use when the user selects PR-Review and Commit or invokes $pr-review-and-commit and explicitly asks to review, make required changes, commit them as ai review, push to the verified PR head branches, and comment on every PR. Do not invoke implicitly or for review-only requests unless the user explicitly selects this skill.
---

# PR-Review and Commit

Use this skill to review a supplied PR set, resolve every accepted finding that can be implemented without guessing, deliver the resulting commits to the existing PR head branches, and leave an accurate summary on each PR.

## Task Naming

After bootstrap metadata and the changed-file list are available, rename the current Codex task once unless the user explicitly says not to:

1. Count distinct PRs after normalizing and deduplicating `{owner, repo, prNumber}` in first-seen order.
2. Derive one concise goal for the complete PR set. Prefer an explicit goal in the user's request, then a confidently inferred common outcome from PR titles, bodies, and changed files, then the first supplied PR's title.
3. Only for a title-derived fallback, strip one leading ticket token matching a bracketed or unbracketed `[A-Za-z][A-Za-z0-9]*-\d+` plus surrounding whitespace and an optional `-`, `:`, `–`, or `—` separator. Never strip ticket-like text elsewhere. If stripping leaves no text, retain the original title.
4. Use `PR Review - <goal>` for one distinct PR and `<N> PRs Review - <goal>` for more than one.
5. Call `codex_app__set_thread_title` once with the computed `title` and omit `threadId` so it targets the current task.

If the title tool is unavailable or fails, or no reliable goal or usable PR title exists, leave the current title unchanged and continue. Task naming is cosmetic and must never block review, fixes, commits, pushes, or comments.

## Authorization Boundary

- Run the mutating workflow only when the current request explicitly authorizes making changes, committing, pushing, and commenting. The plugin's default prompts provide that authorization.
- A bare `$pr-review-and-commit` mention or PR URL without those action words is not push authorization; ask once before delivery.
- An explicit `review only`, `no edits`, `no commit`, `no push`, or `no comments` instruction overrides the default workflow for that action.
- Authorization is limited to the supplied PRs, their verified head repositories and branches, and comments on those PRs. It never authorizes merge, approval, request-changes, close, label, force-push, branch deletion, or a new PR.

## Fast Start

1. Extract every PR URL, normalize it to `{owner, repo, prNumber}`, and deduplicate repeated URLs in first-seen order.
2. Fetch bootstrap metadata: owner/repo/number, title, body, state, base/head refs and SHAs, head repository/owner, fork status, writable head destination, changed-file list, and current review/check context.
3. Apply the task-naming rule, then resolve any workspace and comparison-branch overrides from applicable user or repository instructions. Otherwise search the active workspace roots and use the PR's declared base branch.
4. Locate the local repository by canonical Git remote URL. If no checkout exists, use a disposable clone when safe. Use an isolated disposable worktree for each distinct `{head repository, head ref, head SHA}`; never alter or clean the user's ordinary checkout.
5. Inventory all changed files and hunks, then build the producer-consumer graph across the supplied PR set.
6. Load `references/review-gates.md` and `references/subagents.md`. Run both independent review agents concurrently and reconcile their claims against source evidence.
7. Load `references/fix-policy.md`, accept or reject each finding, and attempt every accepted fix across the supplied PR set. Ask only when required intent, authority, secrets, or an irreversible product/data decision is unavailable.
8. Review the final status and diff by inspection. Do not run lint, builds, tests, package scripts, installs, migrations, or code generation unless the current request explicitly adds them.
9. Load `references/workflow.md` and perform the commit, push, and per-PR comment lifecycle only after all editable PRs reach a final local state.

## Reference Loading

- Load `references/review-gates.md` after the changed-file inventory is known.
- Load `references/subagents.md` before any edit; its two-agent gate is mandatory for every run.
- Load `references/fix-policy.md` before editing, staging, committing, or pushing.
- Load `references/workflow.md` for routing, isolated worktrees, connected-PR coverage, delivery ordering, idempotent comments, and failure handling.

## Non-Negotiables

- Treat every distinct supplied PR as part of one connected review set and cover every changed file and text hunk.
- Honor applicable user or repository routing instructions; otherwise locate repositories by canonical remote in active workspace roots and compare against the declared PR base.
- Use a disposable clone or worktree when an existing checkout cannot be used safely. Stop rather than guessing about an ambiguous repository, fork, comparison branch, or writable destination.
- Prefer GitHub connector/MCP metadata and commenting; use authenticated `gh` only as fallback. Stop rather than guess when metadata or a writable head destination cannot be proven.
- Run two independent concurrent review agents after inventory and before edits. Evidence outranks agent votes.
- Attempt every accepted finding within the supplied PR set, including coordinated and contract-level fixes, while keeping every changed line traceable to a finding.
- Use isolated worktrees, preserve unrelated work, stage explicit intended paths only, and never create an empty commit.
- Commit each distinct changed PR head once with the exact subject `ai review`. Preserve the configured Git author.
- Recheck the remote head immediately before delivery and non-force push only to the verified PR head repository/ref. Never reset, rebase, force-push, bypass hooks, or overwrite concurrent commits.
- Validation defaults to inspection only. Every PR comment must say `Reviewed by inspection` and identify checks not run.
- Post one idempotent timeline summary on every supplied PR, including unchanged, blocked, or partially delivered PRs. Never claim a change was delivered until its push succeeded.

## Default Output

Lead with final outcomes by PR. Include accepted and deferred findings, files changed, commit/push status, comment status, related PR relationships and delivery order, inspection-only validation, partial failures, and remaining risk.
